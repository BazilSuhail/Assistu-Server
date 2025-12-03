from django.urls import path
from . import views

urlpatterns = [
    path('all/', views.get_all_notes, name='get_all_notes'),
    path('create/pdf/', views.create_note_from_pdf, name='create_note_from_pdf'),
    path('create/text/', views.create_note_from_text, name='create_note_from_text'),
    path('search-notes/', views.search_notes, name='search_notes'),

    path('<str:note_id>/', views.get_note_by_id, name='get_note_by_id'),
    path('delete/<str:note_id>', views.delete_note, name='delete_note'),
    # New search endpoint
]