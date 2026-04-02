import stripe
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import Plan, Subscription, Invoice, PaymentMethod

stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')

class SubscriptionService:
    """Service pour gérer les abonnements"""

    @staticmethod
    def create_subscription(user, plan_id, payment_method_id=None):
        """Créer un nouvel abonnement"""
        try:
            plan = Plan.objects.get(id=plan_id)

            # Récupérer ou créer l'organization du user
            membership = user.organization_memberships.first()
            if not membership:
                raise Exception("User must belong to an organization")

            organization = membership.organization

            # Créer un customer Stripe si nécessaire
            stripe_customer_id = SubscriptionService._get_or_create_stripe_customer(
                user, organization
            )

            # Créer l'abonnement Stripe
            stripe_subscription = SubscriptionService._create_stripe_subscription(
                stripe_customer_id,
                plan,
                payment_method_id
            )

            # Créer l'abonnement en base
            subscription = Subscription.objects.create(
                organization=organization,
                user=user,
                plan=plan,
                status=stripe_subscription['status'],
                trial_end=timezone.now() + timedelta(days=plan.trial_days) if plan.trial_days > 0 else None,
                current_period_start=timezone.now(),
                current_period_end=SubscriptionService._calculate_period_end(plan.billing_cycle),
                amount=plan.price,
                currency=plan.currency,
                stripe_subscription_id=stripe_subscription['id'],
                stripe_customer_id=stripe_customer_id
            )

            return subscription

        except Plan.DoesNotExist:
            raise Exception("Plan not found")
        except Exception as e:
            raise Exception(f"Error creating subscription: {str(e)}")

    @staticmethod
    def _get_or_create_stripe_customer(user, organization):
        """Récupérer ou créer un customer Stripe"""
        # Chercher si le customer existe déjà
        existing_subscription = Subscription.objects.filter(
            user=user,
            stripe_customer_id__isnull=False
        ).first()

        if existing_subscription:
            return existing_subscription.stripe_customer_id

        # Créer un nouveau customer
        customer = stripe.Customer.create(
            email=user.email,
            name=user.get_full_name(),
            metadata={
                'user_id': user.id,
                'organization_id': organization.id,
                'organization_name': organization.name
            }
        )

        return customer.id

    @staticmethod
    def _create_stripe_subscription(stripe_customer_id, plan, payment_method_id=None):
        """Créer un abonnement Stripe"""
        subscription_params = {
            'customer': stripe_customer_id,
            'items': [{'price': plan.stripe_price_id}],
            'trial_period_days': plan.trial_days if plan.trial_days > 0 else None,
        }

        if payment_method_id:
            subscription_params['default_payment_method'] = payment_method_id
            subscription_params['payment_behavior'] = 'default_incomplete'

        return stripe.Subscription.create(**subscription_params)

    @staticmethod
    def _calculate_period_end(billing_cycle):
        """Calculer la fin de période selon le cycle"""
        if billing_cycle == 'monthly':
            return timezone.now() + timedelta(days=30)
        elif billing_cycle == 'quarterly':
            return timezone.now() + timedelta(days=90)
        elif billing_cycle == 'yearly':
            return timezone.now() + timedelta(days=365)
        else:
            return timezone.now() + timedelta(days=30)

    @staticmethod
    def cancel_subscription(subscription, cancel_at_period_end=True):
        """Annuler un abonnement"""
        try:
            if cancel_at_period_end:
                # Annuler à la fin de la période
                stripe.Subscription.modify(
                    subscription.stripe_subscription_id,
                    cancel_at_period_end=True
                )
                subscription.cancel_at_period_end = True
            else:
                # Annuler immédiatement
                stripe.Subscription.delete(
                    subscription.stripe_subscription_id
                )
                subscription.status = 'canceled'

            subscription.save()
            return subscription

        except Exception as e:
            raise Exception(f"Error canceling subscription: {str(e)}")

    @staticmethod
    def change_plan(subscription, new_plan_id):
        """Changer le plan d'abonnement"""
        try:
            new_plan = Plan.objects.get(id=new_plan_id)

            # Modifier l'abonnement Stripe
            stripe_subscription = stripe.Subscription.retrieve(
                subscription.stripe_subscription_id
            )

            # Modifier l'item pour utiliser le nouveau prix
            stripe_subscription.items = [{
                'id': stripe_subscription['items']['data'][0].id,
                'price': new_plan.stripe_price_id,
            }]

            updated_stripe_subscription = stripe_subscription.save()

            # Mettre à jour l'abonnement en base
            subscription.plan = new_plan
            subscription.amount = new_plan.price
            subscription.save()

            return subscription

        except Plan.DoesNotExist:
            raise Exception("New plan not found")
        except Exception as e:
            raise Exception(f"Error changing plan: {str(e)}")

    @staticmethod
    def add_payment_method(user, stripe_payment_method_id):
        """Ajouter un moyen de paiement"""
        try:
            # Attacher la méthode de paiement au customer Stripe
            stripe_customer_id = SubscriptionService._get_or_create_stripe_customer(
                user, user.organization_memberships.first().organization
            )

            payment_method = stripe.PaymentMethod.retrieve(stripe_payment_method_id)
            payment_method.attach(customer=stripe_customer_id)

            # Créer en base
            card_details = payment_method.card if hasattr(payment_method, 'card') else None

            db_payment_method = PaymentMethod.objects.create(
                user=user,
                payment_type='card',
                card_last4=card_details.last4 if card_details else '',
                card_brand=card_details.brand if card_details else '',
                card_exp_month=card_details.exp_month if card_details else None,
                card_exp_year=card_details.exp_year if card_details else None,
                stripe_payment_method_id=stripe_payment_method_id
            )

            return db_payment_method

        except Exception as e:
            raise Exception(f"Error adding payment method: {str(e)}")

    @staticmethod
    def set_default_payment_method(payment_method):
        """Définir le moyen de paiement par défaut"""
        try:
            # Mettre tous les moyens de paiement de l'utilisateur à non-default
            PaymentMethod.objects.filter(
                user=payment_method.user
            ).update(is_default=False)

            # Mettre le moyen de paiement sélectionné à default
            payment_method.is_default = True
            payment_method.save()

            return payment_method

        except Exception as e:
            raise Exception(f"Error setting default payment method: {str(e)}")

    @staticmethod
    def create_invoice(subscription):
        """Créer une facture pour un abonnement"""
        try:
            # Générer le numéro de facture
            invoice_number = f"INV-{timezone.now().strftime('%Y%m%d')}-{subscription.id}"

            # Calculer les montants
            subtotal = subscription.amount
            tax_amount = subtotal * 0.20  # 20% TVA (à configurer)
            total = subtotal + tax_amount

            # Créer la facture Stripe
            stripe_invoice = stripe.Invoice.create(
                customer=subscription.stripe_customer_id,
                subscription=subscription.stripe_subscription_id,
                description=f"Facture {invoice_number}"
            )

            # Créer la facture en base
            invoice = Invoice.objects.create(
                organization=subscription.organization,
                subscription=subscription,
                user=subscription.user,
                invoice_number=invoice_number,
                status='draft',
                subtotal=subtotal,
                tax_amount=tax_amount,
                total=total,
                currency=subscription.currency,
                period_start=subscription.current_period_start.date(),
                period_end=subscription.current_period_end.date(),
                due_date=subscription.current_period_end.date(),
                stripe_invoice_id=stripe_invoice.id
            )

            return invoice

        except Exception as e:
            raise Exception(f"Error creating invoice: {str(e)}")
