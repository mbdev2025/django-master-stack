from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def payment_list(request):
    """Liste des paiements (placeholder)"""
    return Response({
        'message': 'Payments module - Use existing Stripe service',
        'payments': []
    })
