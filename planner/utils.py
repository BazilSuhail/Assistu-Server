import json
import requests
from django.conf import settings
from .models import StudyPlan
from bson import ObjectId
from datetime import datetime

# --- LLM Interaction Function ---

def plan_from_llm(user, plan_description):
    """
    Calls the LLM to generate a structured StudyPlan based on the user's description.
    """
    llm_url = getattr(settings, "GROQ_LLM_URL", "https://api.groq.com/openai/v1/chat/completions").strip()
    api_key = settings.GROQ_API_KEY
    
    # Generate schema description for the LLM
    session_schema = json.dumps({
        "subject": "string", 
        "date": "YYYY-MM-DD format (e.g., 2025-01-15)", 
        "goal": "string"
    })
    
    prompt = f"""
    You are a professional study planner. The user wants to create a comprehensive study plan based on this description: "{plan_description}"

    Current date: {datetime.now().strftime("%Y-%m-%d")}

    Return ONLY a valid JSON object with these exact fields:
    {{
        "title": "A concise title for the plan",
        "duration": "A short summary of the plan's length (e.g., 'One Week', 'Five Days')",
        "sessions": [
            # A list of study sessions. Each session must follow this schema: {session_schema}
        ]
    }}

    Example response for 'Plan my python exam review':
    {{
        "title": "Python Final Exam Review",
        "duration": "4 days",
        "sessions": [
            {{
                "subject": "Python Data Structures",
                "date": "2025-12-10",
                "goal": "Review lists, tuples, and dictionaries"
            }},
            {{
                "subject": "Python OOP",
                "date": "2025-12-11",
                "goal": "Master classes, inheritance, and polymorphism"
            }}
        ]
    }}

    Rules:
    - Base the plan's dates on the current date, adjusting for "next week" or "tomorrow" mentioned in the description.
    - Generate at least two sessions unless the description implies a single task.
    - Return ONLY the JSON object, no other text, no markdown formatting, no explanations.
    """

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": prompt},
        ],
        "max_tokens": 1500,
        "temperature": 0.5,
        "response_format": {"type": "json_object"}
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        res = requests.post(llm_url, json=payload, headers=headers, timeout=45)
        res.raise_for_status()
        
        data = res.json()
        content = data["choices"][0]["message"]["content"].strip()
        
        # Clean response (remove markdown fences if LLM fails to honor the prompt)
        if content.startswith('```json'): content = content[7:].strip()
        if content.endswith('```'): content = content[:-3].strip()
        
        event_data = json.loads(content)
        
        # Validate required fields
        required_fields = ['title', 'duration', 'sessions']
        for f in required_fields:
            if f not in event_data:
                raise ValueError(f"LLM response missing required field: {f}")
        
        # Create StudyPlan instance
        study_plan = StudyPlan(
            user=user,
            title=event_data['title'],
            duration=event_data['duration'],
            sessions=event_data['sessions'] # sessions is a ListField of DictField, no special conversion needed
        )
        return study_plan
        
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Failed to connect to LLM service: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error processing LLM response: {str(e)}")


# --- Database Utility Functions ---

def get_plan_by_id(plan_id):
    """Retrieves a single StudyPlan by its ObjectId."""
    try:
        obj_id = ObjectId(plan_id)
    except Exception:
        return None
    return StudyPlan.objects(id=obj_id).first()

def get_plan_by_id_and_user(user, plan_id):
    """Retrieves a single StudyPlan by its ID and ensures user ownership."""
    try:
        obj_id = ObjectId(plan_id)
    except Exception:
        return None
    return StudyPlan.objects(id=obj_id, user=user).first()

def delete_plan(user, plan_id):
    """Deletes a StudyPlan, ensuring user ownership."""
    plan = get_plan_by_id_and_user(user, plan_id)
    if not plan:
        raise ValueError("StudyPlan not found or access denied")
    plan.delete()
    return True

def get_user_plans(user):
    """Retrieves all StudyPlans for a given user."""
    # Orders by creation date, most recent first
    return list(StudyPlan.objects(user=user).order_by('-created_at'))