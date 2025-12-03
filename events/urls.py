from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_events, name='list_events'),
    path('create/', views.create_event, name='create_event'),
    path('<str:event_id>/', views.event_detail, name='event_detail'),
    path('update/<str:event_id>/', views.edit_event, name='edit_event'),
    path('delete/<str:event_id>/', views.remove_event, name='remove_event'),
]