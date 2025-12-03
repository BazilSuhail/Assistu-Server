import json
import requests
from django.conf import settings
from .models import Event
from datetime import datetime, timedelta
from bson import ObjectId  # for ObjectId validation


def plan_event_from_llm(user, event_description):
    llm_url = getattr(settings, "GROQ_LLM_URL", "https://api.groq.com/openai/v1/chat/completions").strip()
    api_key = settings.GROQ_API_KEY

    # Get current date for context
    current_date = datetime.now().strftime("%Y-%m-%d")
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    prompt = f"""
    You are a professional event planner. The user wants to create an event based on this description: "{event_description}"

    Current date and time: {current_datetime}
    Today's date: {current_date}

    Return ONLY a valid JSON object with these exact fields:
    {{
        "title": "string",
        "description": "string",
        "event_type": "study_session|class|meeting|exam",
        "start_time": "YYYY-MM-DDTHH:MM:SS.sssZ format",
        "end_time": "YYYY-MM-DDTHH:MM:SS.sssZ format"
    }}

    Example response:
    {{
        "title": "Math Exam Review",
        "description": "Review calculus chapters 1-3 for exam",
        "event_type": "study_session",
        "start_time": "2025-01-15T10:00:00Z",
        "end_time": "2025-01-15T12:00:00Z"
    }}

    Rules:
    - event_type must be one of: study_session, class, meeting, exam
    - If the description mentions "today", use today's date ({current_date})
    - If the description mentions "tomorrow", use tomorrow's date
    - If the description mentions "next week", use a date within the next 7 days
    - If the description mentions "next month", use a date within the next 30 days
    - If no specific time is mentioned, suggest a realistic time relative to today
    - Duration should be realistic (1-2 hours for study sessions, 1 hour for meetings, etc.)
    - Return ONLY the JSON object, no other text, no markdown formatting, no explanations.
    """

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": prompt},
        ],
        "max_tokens": 500,
        "temperature": 0.2,
        "response_format": {"type": "json_object"}  # Force JSON response
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        res = requests.post(llm_url, json=payload, headers=headers, timeout=30)
        res.raise_for_status()
        
        data = res.json()
        
        if "choices" not in data or len(data["choices"]) == 0:
            raise ValueError("Invalid API response: no choices returned")
        
        content = data["choices"][0]["message"]["content"]
        
        if not content:
            raise ValueError("Empty response from LLM")
        
        print(f"Raw LLM response: {content}")  # Debug
        
        # Clean the response - remove any markdown code blocks
        content = content.strip()
        if content.startswith('```json'):
            content = content[7:]  # Remove ```json
        if content.startswith('```'):
            content = content[3:]  # Remove ```
        if content.endswith('```'):
            content = content[:-3]  # Remove ```
        content = content.strip()
        
        if not content:
            raise ValueError("Cleaned response is empty")
        
        try:
            event_data = json.loads(content)
        except json.JSONDecodeError:
            print(f"Failed to parse JSON: {content}")
            raise ValueError(f"Invalid JSON response from LLM")
        
        # Validate required fields
        required_fields = ['title', 'event_type', 'start_time', 'end_time']
        for f in required_fields:
            if f not in event_data:
                raise ValueError(f"LLM response missing required field: {f}")

        # Validate field values
        valid_types = ['study_session', 'class', 'meeting', 'exam']
        
        if event_data.get('event_type') not in valid_types:
            event_data['event_type'] = 'study_session'  # default fallback

        # Parse start_time and end_time with multiple format support
        start_time_str = str(event_data['start_time'])
        end_time_str = str(event_data['end_time'])
        
        date_formats = [
            '%Y-%m-%dT%H:%M:%S.%fZ',  # 2025-01-15T10:00:00.000Z
            '%Y-%m-%dT%H:%M:%SZ',     # 2025-01-15T10:00:00Z
            '%Y-%m-%d %H:%M:%S',      # 2025-01-15 10:00:00
            '%Y-%m-%d %H:%M',         # 2025-01-15 10:00
            '%Y-%m-%d',               # 2025-01-15
        ]
        
        parsed_start_time = None
        parsed_end_time = None
        
        # Parse start_time
        for fmt in date_formats:
            try:
                parsed_start_time = datetime.strptime(start_time_str, fmt)
                break
            except ValueError:
                continue
        
        if parsed_start_time is None:
            # Default to tomorrow if parsing fails
            parsed_start_time = datetime.now() + timedelta(days=1)
        
        # Parse end_time
        for fmt in date_formats:
            try:
                parsed_end_time = datetime.strptime(end_time_str, fmt)
                break
            except ValueError:
                continue
        
        if parsed_end_time is None:
            # Default to start_time + 1 hour if parsing fails
            parsed_end_time = parsed_start_time + timedelta(hours=1)
        
        # Ensure end_time is after start_time
        if parsed_end_time <= parsed_start_time:
            parsed_end_time = parsed_start_time + timedelta(hours=1)
        
        # Set the parsed times
        event_data['start_time'] = parsed_start_time
        event_data['end_time'] = parsed_end_time

        # Set defaults for optional fields (but don't include fields not in the model)
        event_data.setdefault('description', event_description)

        # Create Event instance - only use fields that exist in the Event model
        event = Event(
            user=user,
            title=event_data['title'],
            description=event_data['description'],
            event_type=event_data['event_type'],
            start_time=event_data['start_time'],
            end_time=event_data['end_time']
        )
        return event
        
    except requests.exceptions.RequestException as e:
        print(f"API request error: {e}")
        raise ValueError(f"Failed to connect to LLM service: {str(e)}")
    except Exception as e:
        print(f"Error in plan_event_from_llm: {e}")
        raise

def get_event_by_id(event_id):
    try:
        obj_id = ObjectId(event_id)
    except Exception:
        return None
    return Event.objects(id=obj_id).first()

def delete_event(user, event_id):
    event = get_event_by_id(event_id)
    print(event)
    if not event or event.user.id != user.id:
        raise ValueError("Event not found or access denied")
    event.delete()
    return True

def update_event(user, event_id, update_data):
    event = get_event_by_id(event_id)
    if not event or event.user.id != user.id:
        raise ValueError("Event not found or access denied")
    
    for key, value in update_data.items():
        if hasattr(event, key):
            if key in ["start_time", "end_time"]:
                # Handle datetime conversion
                if isinstance(value, str):
                    # Add more parsing logic if needed
                    try:
                        value = datetime.fromisoformat(value.replace('Z', '+00:00'))
                    except ValueError:
                        # If parsing fails, keep original value or use default
                        continue
            setattr(event, key, value)
    event.save()
    return event

def get_user_events(user):
    return list(Event.objects(user=user))