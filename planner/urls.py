from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_and_create_plan, name='study_plan_list_create'),
    
    # GET: Detail view for a specific plan
    path('<str:plan_id>/', views.plan_detail, name='study_plan_detail'),
    
    path('delete/<str:plan_id>', views.remove_plan, name='study_plan_delete'),
]