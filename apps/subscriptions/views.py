from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def subscription_list(request):
    """Liste des abonnements (placeholder)"""
    return Response({
        'message': 'Subscription module - À implémenter',
        'subscriptions': []
    })
