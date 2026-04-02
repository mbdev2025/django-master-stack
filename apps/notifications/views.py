from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from .models import Notification, NotificationPreference, EmailTemplate, NotificationLog
from .serializers import (
    NotificationSerializer, NotificationPreferenceSerializer,
    EmailTemplateSerializer, NotificationLogSerializer
)
from .services import NotificationService

class NotificationViewSet(viewsets.ModelViewSet):
    """ViewSet pour les notifications"""
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Notification.objects.filter(user=user).select_related('organization')

    @action(detail=False, methods=['get'])
    def unread(self, request):
        """Notifications non lues"""
        user = request.user
        unread = Notification.objects.filter(
            user=user,
            is_read=False
        ).order_by('-created_at')

        serializer = self.get_serializer(unread, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Marquer toutes les notifications comme lues"""
        user = request.user
        count = Notification.objects.filter(
            user=user,
            is_read=False
        ).update(is_read=True, read_at=timezone.now())

        return Response({'marked_read': count})

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Marquer une notification comme lue"""
        notification = self.get_object()
        notification.mark_as_read()

        return Response({'status': 'marked_as_read'})

    @action(detail=False, methods=['post'])
    def send(self, request):
        """Envoyer une notification (test/admin)"""
        try:
            recipient_id = request.data.get('user_id')
            title = request.data.get('title')
            message = request.data.get('message')
            notification_type = request.data.get('type', 'info')

            if not all([recipient_id, title, message]):
                return Response({'error': 'user_id, title, message requis'}, status=400)

            notification = NotificationService.send_notification(
                user_id=recipient_id,
                title=title,
                message=message,
                notification_type=notification_type,
                organization=request.user.organization_memberships.first().organization
            )

            return Response(
                NotificationSerializer(notification).data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response({'error': str(e)}, status=400)

class NotificationPreferenceViewSet(viewsets.ModelViewSet):
    """ViewSet pour les préférences de notification"""
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return NotificationPreference.objects.filter(user=user)

    @action(detail=False, methods=['get', 'post'])
    def my_preferences(self, request):
        """Préférences de l'utilisateur actuel"""
        if request.method == 'GET':
            preferences, created = NotificationPreference.objects.get_or_create(
                user=request.user
            )
            return Response(NotificationPreferenceSerializer(preferences).data)
        else:
            # POST pour mettre à jour
            preferences, created = NotificationPreference.objects.get_or_create(
                user=request.user
            )
            serializer = NotificationPreferenceSerializer(
                preferences,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

class EmailTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet pour les templates d'emails"""
    serializer_class = EmailTemplateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return EmailTemplate.objects.filter(
            organization__members__user=user
        ).select_related('organization')

class NotificationLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour les logs de notifications"""
    serializer_class = NotificationLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return NotificationLog.objects.filter(
            notification__user=user
        ) if user.is_staff else NotificationLog.objects.none()
