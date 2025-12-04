from django.urls import path
from . import views

urlpatterns = [
    # Create task via LLM
    path('create/', views.create_task, name='create_task'),
    
    # Delete a task
    path('delete/', views.delete_task_view, name='delete_task'),
    
    # Update a task
    path('update/', views.update_task_view, name='update_task'),
    
    # Get all tasks for logged-in user
    path('user/', views.user_tasks_view, name='user_tasks'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Get single task by ID
    path('<str:task_id>/', views.task_detail_view, name='task_detail'),
]
