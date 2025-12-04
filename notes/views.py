from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import parser_classes
from .models import Note
from .utils import process_pdf_note, create_note_from_text
from bson import ObjectId

from .allMiniLm_utils import search_similar_notes

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_notes(request):
    user = request.user
    notes = Note.objects(user=user)
    return Response({
        'notes': [{
            'id': str(n.id),
            'title': n.title,
            'subject': n.subject,
            'importance': n.importance,
            'created_at': n.created_at
        } for n in notes]
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_note_by_id(request, note_id):
    user = request.user
    try:
        note = Note.objects(id=ObjectId(note_id), user=user).first()
        if not note:
            return Response({'error': 'Note not found'}, status=404)
        
        return Response({
            'id': str(note.id),
            'title': note.title,
            'transcript': note.transcript,
            'summary': note.summary,
            'subject': note.subject,
            'categories': note.categories,
            'keywords': note.keywords,
            'explanation': note.explanation,
            'importance': note.importance,
            'tags': note.tags,
            'created_at': note.created_at,
            'updated_at': note.updated_at
        })
    except Exception:
        return Response({'error': 'Invalid note ID'}, status=400)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def create_note_from_pdf(request):
    user = request.user
    
    if 'file' not in request.FILES:
        return Response({'error': 'PDF file is required'}, status=400)
    
    pdf_file = request.FILES['file']
    
    # Check if file is PDF by extension and content type
    if not pdf_file.name.lower().endswith('.pdf'):
        return Response({'error': 'File must be a PDF'}, status=400)
    
    # Check content type
    if not pdf_file.content_type == 'application/pdf':
        return Response({'error': 'File must be a PDF'}, status=400)
    
    # Optional: Check file size (e.g., max 10MB)
    if pdf_file.size > 10 * 1024 * 1024:  # 10MB
        return Response({'error': 'File size too large (max 10MB)'}, status=400)
    
    title = request.data.get('title', 'Untitled Note')
    subject = request.data.get('subject', 'General')
    
    try:
        note = process_pdf_note(user, pdf_file, title, subject)
        return Response({
            'message': 'Note created from PDF',
            'id': str(note.id),
            'title': note.title
        })
    except Exception as e:
        return Response({'error': str(e)}, status=400)
    

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_note_from_text(request):
    user = request.user
    title = request.data.get('title')
    text = request.data.get('text', '')
    subject = request.data.get('subject', 'General')
    
    if not title:
        return Response({'error': 'Title is required'}, status=400)
    
    if not text:
        return Response({'error': 'Text content is required'}, status=400)
    
    try:
        note = create_note_from_text(user, title, text, subject)
        return Response({
            'message': 'Note created',
            'id': str(note.id),
            'title': note.title
        })
    except Exception as e:
        return Response({'error': str(e)}, status=400)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_note(request, note_id):
    user = request.user
    try:
        note = Note.objects(id=ObjectId(note_id), user=user).first()
        if not note:
            return Response({'error': 'Note not found'}, status=404)
        
        note.delete()
        return Response({'message': 'Note deleted'})
    except Exception:
        return Response({'error': 'Invalid note ID'}, status=400)
    
# ---------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def search_notes(request):
    """
    Search notes using semantic similarity
    
    Request body:
    {
        "query": "search text",
        "threshold": 0.2  // optional, default 0.2 (20% similarity)
    }
    """
    user = request.user
    query = request.data.get('query', '').strip()
    threshold = float(request.data.get('threshold', 0.2))
    
    if not query:
        return Response({'error': 'Query text is required'}, status=400)
    
    # Validate threshold
    if not 0 <= threshold <= 1:
        return Response({'error': 'Threshold must be between 0 and 1'}, status=400)
    
    results = search_similar_notes(user, query, threshold)
        
    return Response({
            'query': query,
            'threshold': threshold,
            'count': len(results),
            'results': [{
                'id': str(result['note'].id),
                'title': result['note'].title,
                'subject': result['note'].subject,
                'summary': result['note'].summary,
                'importance': result['note'].importance,
                'similarity': result['similarity'],
                'created_at': result['note'].created_at,
                'keywords': result['note'].keywords,
                'tags': result['note'].tags
            } for result in results]
    })

# def search_notes(request):
#     """
#     Search notes using semantic similarity
    
#     Request body:
#     {
#         "query": "search text",
#         "threshold": 0.2  // optional, default 0.2 (20% similarity)
#     }
#     """
#     user = request.user
#     query = request.data.get('query', '').strip()
#     threshold = float(request.data.get('threshold', 0.2))
    
#     if not query:
#         return Response({'error': 'Query text is required'}, status=400)
    
#     # Validate threshold
#     if not 0 <= threshold <= 1:
#         return Response({'error': 'Threshold must be between 0 and 1'}, status=400)
#     try:
#         from .allMiniLm_utils import search_similar_notes
        
#         results = search_similar_notes(user, query, threshold)
        
#         return Response({
#             'query': query,
#             'threshold': threshold,
#             'count': len(results),
#             'results': [{
#                 'id': str(result['note'].id),
#                 'title': result['note'].title,
#                 'subject': result['note'].subject,
#                 'summary': result['note'].summary,
#                 'importance': result['note'].importance,
#                 'similarity': result['similarity'],
#                 'created_at': result['note'].created_at,
#                 'keywords': result['note'].keywords,
#                 'tags': result['note'].tags
#             } for result in results]
#         })
#     except Exception as e:
#         return Response({'error': f'Search failed: {str(e)}'}, status=500)