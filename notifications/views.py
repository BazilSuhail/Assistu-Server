from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Notification

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notification_list(request):
    user_id = request.auth.payload.get('user_id')
    
    notifications = Notification.objects.filter(user=user_id)
    return Response({'notifications': [{
        'id': str(n.id),
        'title': n.title,
        'message': n.message,
        'type': n.type
    } for n in notifications]})