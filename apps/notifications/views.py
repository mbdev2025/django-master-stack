from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notification_list(request):
    """Liste des notifications (placeholder)"""
    return Response({
        'message': 'Notifications module - À implémenter',
        'notifications': []
    })
