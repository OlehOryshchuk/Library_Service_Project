from celery import shared_task

from .models import Payment
from .stripe_api import StripeSessionHandler


@shared_task
def check_stripe_session_status():
    payments = Payment.objects.all()
    # session_is_expired returns True if expired
    # and updates the payment status else return False
    for payment in payments:
        StripeSessionHandler.session_is_expired(payment)
