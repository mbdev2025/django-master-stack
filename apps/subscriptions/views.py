from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta

from .models import Plan, Subscription, Invoice, PaymentMethod, UsageRecord
from .serializers import (
    PlanSerializer, SubscriptionSerializer, InvoiceSerializer,
    PaymentMethodSerializer, UsageRecordSerializer
)
from .services import SubscriptionService

class PlanViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour les plans d'abonnement"""
    serializer_class = PlanSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Plan.objects.filter(is_active=True)

    @action(detail=True, methods=['get'])
    def features(self, request, pk=None):
        """Obtenir les fonctionnalités d'un plan"""
        plan = self.get_object()
        return Response({
            'plan': PlanSerializer(plan).data,
            'features': plan.features,
            'limits': {
                'max_users': plan.max_users,
                'max_storage_gb': plan.max_storage_gb,
                'api_calls_per_month': plan.api_calls_per_month,
            }
        })

class SubscriptionViewSet(viewsets.ModelViewSet):
    """ViewSet pour les abonnements"""
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Subscription.objects.filter(
            organization__members__user=user
        ).select_related('plan')

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Obtenir l'abonnement actif de l'utilisateur"""
        user = request.user
        try:
            subscription = Subscription.objects.filter(
                user=user,
                status='active'
            ).select_related('plan').first()

            if subscription:
                return Response(SubscriptionSerializer(subscription).data)
            else:
                return Response({'detail': 'Aucun abonnement actif'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=400)

    @action(detail=False, methods=['post'])
    def subscribe(self, request):
        """Créer un nouvel abonnement"""
        try:
            plan_id = request.data.get('plan_id')
            payment_method_id = request.data.get('payment_method_id')

            if not plan_id:
                return Response({'error': 'plan_id requis'}, status=400)

            subscription = SubscriptionService.create_subscription(
                user=request.user,
                plan_id=plan_id,
                payment_method_id=payment_method_id
            )

            return Response(
                SubscriptionSerializer(subscription).data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response({'error': str(e)}, status=400)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Annuler un abonnement"""
        try:
            subscription = self.get_object()
            cancel_at_period_end = request.data.get('cancel_at_period_end', True)

            updated_subscription = SubscriptionService.cancel_subscription(
                subscription,
                cancel_at_period_end=cancel_at_period_end
            )

            return Response(SubscriptionSerializer(updated_subscription).data)
        except Exception as e:
            return Response({'error': str(e)}, status=400)

    @action(detail=True, methods=['post'])
    def upgrade(self, request, pk=None):
        """Upgrader vers un plan supérieur"""
        try:
            subscription = self.get_object()
            new_plan_id = request.data.get('new_plan_id')

            if not new_plan_id:
                return Response({'error': 'new_plan_id requis'}, status=400)

            updated_subscription = SubscriptionService.change_plan(
                subscription,
                new_plan_id
            )

            return Response(SubscriptionSerializer(updated_subscription).data)
        except Exception as e:
            return Response({'error': str(e)}, status=400)

class InvoiceViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour les factures"""
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Invoice.objects.filter(
            organization__members__user=user
        ).select_related('subscription')

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Télécharger la facture PDF"""
        invoice = self.get_object()
        if invoice.invoice_pdf:
            # Retourner le fichier PDF
            from django.http import FileResponse
            return FileResponse(invoice.invoice_pdf, content_type='application/pdf')
        else:
            return Response({'error': 'PDF non disponible'}, status=404)

class PaymentMethodViewSet(viewsets.ModelViewSet):
    """ViewSet pour les moyens de paiement"""
    serializer_class = PaymentMethodSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PaymentMethod.objects.filter(user=self.request.user)

    @action(detail=False, methods=['post'])
    def add(self, request):
        """Ajouter un moyen de paiement"""
        try:
            payment_method_id = request.data.get('payment_method_id')

            if not payment_method_id:
                return Response({'error': 'payment_method_id requis'}, status=400)

            payment_method = SubscriptionService.add_payment_method(
                user=request.user,
                stripe_payment_method_id=payment_method_id
            )

            return Response(
                PaymentMethodSerializer(payment_method).data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response({'error': str(e)}, status=400)

    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """Définir comme moyen de paiement par défaut"""
        try:
            payment_method = self.get_object()
            updated = SubscriptionService.set_default_payment_method(payment_method)
            return Response(PaymentMethodSerializer(updated).data)
        except Exception as e:
            return Response({'error': str(e)}, status=400)

class UsageRecordViewSet(viewsets.ModelViewSet):
    """ViewSet pour les enregistrements d'usage"""
    serializer_class = UsageRecordSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return UsageRecord.objects.filter(
            subscription__user=user
        ).select_related('subscription')
