import json
import requests
from django.conf import settings
from .models import Task
from datetime import datetime
from bson import ObjectId  # for ObjectId validation

def generate_task_from_llm(user, task_description):
    llm_url = getattr(settings, "GROQ_LLM_URL", "https://api.groq.com/openai/v1/chat/completions").strip()
    api_key = settings.GROQ_API_KEY

    prompt = f"""
    You are a professional task planner. The user wants to create a task with this description: "{task_description}"

    Return ONLY a valid JSON object with these exact fields:
    {{
        "title": "string",
        "description": "string",
        "subject": "string",
        "type": "assignment|study|project|exam",
        "priority": "low|medium|high",
        "status": "pending",
        "due_date": "YYYY-MM-DDTHH:MM:SS.sssZ format",
        "estimated_duration": number (minutes),
        "tags": ["array", "of", "strings"],
        "original_command": "the original task description"
    }}

    Example response:
    {{
        "title": "Complete project proposal",
        "description": "Write and submit the final project proposal",
        "subject": "Computer Science",
        "type": "project",
        "priority": "high",
        "status": "pending",
        "due_date": "2025-01-15T10:00:00Z",
        "estimated_duration": 120,
        "tags": ["urgent", "proposal", "cs"],
        "original_command": "{task_description}"
    }}

    IMPORTANT: Return ONLY the JSON object, no other text, no markdown formatting, no explanations.
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
            task_data = json.loads(content)
        except json.JSONDecodeError:
            print(f"Failed to parse JSON: {content}")
            raise ValueError(f"Invalid JSON response from LLM")
        
        # Validate required fields
        required_fields = ['title', 'subject', 'type', 'priority', 'status', 'due_date']
        for f in required_fields:
            if f not in task_data:
                raise ValueError(f"LLM response missing required field: {f}")

        # Validate field values
        valid_types = ['assignment', 'study', 'project', 'exam']
        valid_priorities = ['low', 'medium', 'high']
        valid_statuses = ['pending', 'in_progress', 'completed', 'cancelled']
        
        if task_data.get('type') not in valid_types:
            task_data['type'] = 'assignment'  # default fallback
        if task_data.get('priority') not in valid_priorities:
            task_data['priority'] = 'medium'  # default fallback
        if task_data.get('status') not in valid_statuses:
            task_data['status'] = 'pending'  # default fallback

        # Parse due_date with multiple format support
        due_date_str = str(task_data['due_date'])
        date_formats = [
            '%Y-%m-%dT%H:%M:%S.%fZ',  # 2025-01-15T10:00:00.000Z
            '%Y-%m-%dT%H:%M:%SZ',     # 2025-01-15T10:00:00Z
            '%Y-%m-%d %H:%M:%S',      # 2025-01-15 10:00:00
            '%Y-%m-%d',               # 2025-01-15
        ]
        
        parsed_date = None
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(due_date_str, fmt)
                break
            except ValueError:
                continue
        
        if parsed_date is None:
            # Default to tomorrow if parsing fails
            parsed_date = datetime.now() + timedelta(days=1)
        
        task_data['due_date'] = parsed_date

        # Set defaults for optional fields
        task_data.setdefault('description', task_description)
        task_data.setdefault('estimated_duration', 60)
        task_data.setdefault('tags', [])
        task_data.setdefault('original_command', task_description)

        # Ensure tags is a list
        if not isinstance(task_data['tags'], list):
            task_data['tags'] = []

        # Create Task instance
        task = Task(user=user, **task_data)
        return task
        
    except requests.exceptions.RequestException as e:
        print(f"API request error: {e}")
        raise ValueError(f"Failed to connect to LLM service: {str(e)}")
    except Exception as e:
        print(f"Error in generate_task_from_llm: {e}")
        raise

def get_task_by_id(task_id):
    try:
        obj_id = ObjectId(task_id)
    except Exception:
        return None
    return Task.objects(id=obj_id).first()


def delete_task(user, task_id):
    task = get_task_by_id(task_id)
    if not task or task.user.id != user.id:
        raise ValueError("Task not found or access denied")
    task.delete()
    return True


def update_task(user, task_id, update_data):
    task = get_task_by_id(task_id)
    if not task or task.user.id != user.id:
        raise ValueError("Task not found or access denied")
    
    for key, value in update_data.items():
        if hasattr(task, key):
            if key == "due_date":
                value = datetime.fromisoformat(value)
            setattr(task, key, value)
    task.save()
    return task


def get_user_tasks(user):
    return list(Task.objects(user=user))
