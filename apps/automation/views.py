from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def automation_list(request):
    """Liste des automatisations N8N (placeholder)"""
    return Response({
        'message': 'Automation module - Use existing N8N client',
        'automations': []
    })
