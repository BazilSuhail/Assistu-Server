from rest_framework import status
from rest_framework.decorators import api_view
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


# @api_view(['POST'])
# def register(request):
#     email = request.data.get('email')
#     password = request.data.get('password')
#     name = request.data.get('name')

#     if User.objects.filter(email=email).first():
#         return Response({'error': 'User already exists'}, status=400)

#     username = format_username(name)

#     user = User(email=email, name=name, username=username)
#     user.set_password(password)
#     user.save()

#     refresh = RefreshToken()
#     refresh['user_id'] = str(user.id)
#     # refresh = RefreshToken.for_user(user)

#     return Response({
#         'message': 'User created',
#         'user': {
#             'id': str(user.id),
#             'email': user.email,
#             'name': user.name,
#             'username': user.username
#         },
#         'access': str(refresh.access_token),
#         'refresh': str(refresh)
#     })


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
