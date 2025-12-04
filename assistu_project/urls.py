from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # path('admin/', admin.site.urls),
    # path('api/', include('assistu.urls')),
    path('api/auth/', include('users.urls')),
    path('api/tasks/', include('tasks.urls')),
    path('api/events/', include('events.urls')),
    path('api/notes/', include('notes.urls')),
    path('api/planner/', include('planner.urls')),
    path('api/notifications/', include('notifications.urls')),
]