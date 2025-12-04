from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from datetime import datetime, timedelta

from notes.models import Note
from tasks.models import Task
from events.models import Event
from planner.models import StudyPlan

from .utils import generate_task_from_llm, delete_task, update_task, get_user_tasks, get_task_by_id

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_task(request):
    user = request.user
    task_description = request.data.get('description')
    if not task_description:
        return Response({"error": "Missing task description"}, status=400)
    
    try: 
        task = generate_task_from_llm(user, task_description)
        task.save()
        return Response({"message": "Task created with title", "id": str(task.id), "title": str(task.title)})
    except Exception as e:
        return Response({"error": str(e)}, status=400)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_task_view(request):
    user = request.user
    task_id = request.data.get('id')
    try:
        delete_task(user, task_id)
        return Response({"message": "Task deleted"})
    except Exception as e:
        return Response({"error": str(e)}, status=400)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_task_view(request):
    user = request.user
    task_id = request.data.get('id')
    update_data = request.data.get('update', {})
    try:
        task = update_task(user, task_id, update_data)
        return Response({"message": "Task updated", "task": {
            "id": str(task.id),
            "title": task.title,
            "subject": task.subject,
            "status": task.status
        }})
    except Exception as e:
        return Response({"error": str(e)}, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_tasks_view(request):
    user = request.user
    tasks = get_user_tasks(user)
    return Response({"tasks": [{
        "id": str(t.id),
        "title": t.title,
        "subject": t.subject,
        "status": t.status,
        "priority": t.priority,
        "due_date": t.due_date
    } for t in tasks]})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def task_detail_view(request, task_id):
    task = get_task_by_id(task_id)
    if not task or task.user.id != request.user.id:
        return Response({"error": "Task not found or access denied"}, status=404)
    
    return Response({
        "id": str(task.id),
        "title": task.title,
        "description": task.description,
        "subject": task.subject,
        "type": task.type,
        "priority": task.priority,
        "status": task.status,
        "due_date": task.due_date,
        "estimated_duration": task.estimated_duration,
        "tags": task.tags,
        "original_command": task.original_command
    })


# dashboard

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard(request):
    user = request.user
    now = datetime.now()
    
    # Calculate next month's date range
    next_month_end = now + timedelta(days=30)
    
    # Get all notes for the user
    all_notes = Note.objects(user=user.id).order_by('-created_at')
    notes_count = all_notes.count()
    
    notes_data = [
        {
            "id": str(n.id),
            "title": n.title,
            "transcript": n.transcript,
            "summary": n.summary,
            "explanation": n.explanation,
            "subject": n.subject,
            "categories": n.categories,
            "keywords": n.keywords,
            "importance": n.importance,
            "tags": n.tags,
            "created_at": n.created_at,
            "updated_at": n.updated_at
        }
        for n in all_notes
    ]
    
    # Get all tasks within the next month
    tasks_next_month = Task.objects(
        user=user.id,
        due_date__gte=now,
        due_date__lte=next_month_end
    ).order_by('due_date')
    
    tasks_data = [
        {
            "id": str(t.id),
            "title": t.title,
            "description": t.description,
            "subject": t.subject,
            "type": t.type,
            "priority": t.priority,
            "status": t.status,
            "due_date": t.due_date,
            "estimated_duration": t.estimated_duration,
            "tags": t.tags,
            "created_at": t.created_at,
            "updated_at": t.updated_at,
            "completed_at": t.completed_at,
            "original_command": t.original_command
        }
        for t in tasks_next_month
    ]
    
    # Get all events within the next month
    events_next_month = Event.objects(
        user=user.id,
        start_time__gte=now,
        start_time__lte=next_month_end
    ).order_by('start_time')
    
    events_data = [
        {
            "id": str(e.id),
            "title": e.title,
            "description": e.description,
            "event_type": e.event_type,
            "start_time": e.start_time,
            "end_time": e.end_time,
            "related_task": str(e.related_task.id) if e.related_task else None,
            "created_at": e.created_at
        }
        for e in events_next_month
    ]
    
    # Get all study plans (event plans) within the next month
    # Note: StudyPlan doesn't have a date field, so we'll get all plans for the user
    # If you want to filter by date, you'll need to add a date field to StudyPlan model
    study_plans = StudyPlan.objects(user=user.id).order_by('-created_at')
    
    plans_data = [
        {
            "id": str(p.id),
            "title": p.title,
            "duration": p.duration,
            "sessions": p.sessions,
            "created_at": p.created_at,
            "updated_at": p.updated_at
        }
        for p in study_plans
    ]
    
    return Response({
        "notes_count": notes_count,
        "notes": notes_data,
        "tasks_next_month": tasks_data,
        "events_next_month": events_data,
        "study_plans": plans_data
    })