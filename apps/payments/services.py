import stripe
from django.conf import settings

stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')

class StripeService:
    @staticmethod
    def create_checkout(customer_email, price_id, success_url):
        return stripe.checkout.Session.create(
            customer_email=customer_email,
            line_items=[{'price': price_id, 'quantity': 1}],
            mode='subscription',
            success_url=success_url,
        )
