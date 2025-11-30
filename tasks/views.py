from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from datetime import datetime

from notes.models import Note
from tasks.models import Task
from events.models import Event

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
        return Response({"message": "Task created", "id": str(task.id)})
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
    print("ahhaahah")

    user = request.user
    print(user)
    now = datetime.now()

    # Tasks due today
    start_day = datetime(now.year, now.month, now.day)
    end_day = start_day + timedelta(days=1)

    tasks_due_today = Task.objects(
        user=user.id,
        due_date__gte=start_day,
        due_date__lt=end_day
    ).count()

    # Upcoming events
    upcoming_events = Event.objects(
        user=user.id,
        start_time__gte=now
    ).count()

    # Study hours tracked
    # You track study hours through Task.estimated_duration (in minutes)
    completed_tasks = Task.objects(
        user=user.id,
        status="completed"
    )

    study_minutes = sum(t.estimated_duration for t in completed_tasks)
    study_hours = round(study_minutes / 60, 2)

    # Notes created
    notes_count = Note.objects(user=user.id).count()

    # Recent tasks
    recent_tasks = Task.objects(user=user.id).order_by('-created_at')[:5]
    recent_tasks_data = [
        {
            "title": t.title,
            "due_date": t.due_date,
            "priority": t.priority
        }
        for t in recent_tasks
    ]

    # Recent notes
    recent_notes = Note.objects(user=user.id).order_by('-created_at')[:5]
    recent_notes_data = [
        {
            "title": n.title,
            "created_at": n.created_at,
            "duration": len(n.transcript.split()) if n.transcript else 0
        }
        for n in recent_notes
    ]

    return Response({
        "tasks_due_today": tasks_due_today,
        "upcoming_events": upcoming_events,
        "study_hours": study_hours,
        "notes_created": notes_count,
        "recent_tasks": recent_tasks_data,
        "recent_notes": recent_notes_data
    })