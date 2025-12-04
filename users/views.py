from rest_framework import status 
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
import datetime

from notes.models import Note
from tasks.models import Task
from events.models import Event

def format_username(name):
    return " ".join(w.capitalize() for w in name.split())

@api_view(['POST'])
def register(request):
    email = request.data.get('email')
    password = request.data.get('password')
    name = request.data.get('name')
    course_name = request.data.get('courseName')

    if User.objects.filter(email=email).first():
        return Response({'error': 'User already exists'}, status=400)

    username = format_username(name)

    subjects_list = []
    if course_name:
        subjects_list.append(course_name)

    user = User(
        email=email,
        name=name,
        username=username,
        subjects=subjects_list
    )
    user.set_password(password)
    user.save()

    refresh = RefreshToken()
    refresh['user_id'] = str(user.id)

    return Response({
        'message': 'User created',
        'user': {
            'id': str(user.id),
            'email': user.email,
            'name': user.name,
            'username': user.username,
            'subjects': user.subjects
        },
        'access': str(refresh.access_token),
        'refresh': str(refresh)
    })


@api_view(['POST'])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    user = User.objects.filter(email=email).first()

    if user and user.check_password(password):
        refresh = RefreshToken()
        refresh['user_id'] = str(user.id)

        return Response({
            'message': 'Login successful',
            'user': {
                'id': str(user.id),
                'email': user.email,
                'name': user.name,
                'username': user.username
            },
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        })

    return Response({'error': 'Invalid credentials'}, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    """
    Get authenticated user's profile data with statistics
    Requires: Authorization header with Bearer token
    """
    user = request.user
    
    # Calculate user statistics
    total_notes = Note.objects(user=user.id).count()
    total_tasks = Task.objects(user=user.id).count()
    total_events = Event.objects(user=user.id).count()
    
    # Count completed tasks
    completed_tasks = Task.objects(user=user.id, status='completed').count()
    
    # Count pending tasks
    pending_tasks = Task.objects(user=user.id, status='pending').count()
    
    return Response({
        'profile': {
            'id': str(user.id),
            'email': user.email,
            'name': user.name,
            'username': user.username,
            'subjects': user.subjects,
            'theme': user.theme,
            'avatar': user.avatar,
            'created_at': user.created_at,
            'updated_at': user.updated_at
        },
        'statistics': {
            'total_notes': total_notes,
            'total_tasks': total_tasks,
            'total_events': total_events,
            'completed_tasks': completed_tasks,
            'pending_tasks': pending_tasks
        }
    })
