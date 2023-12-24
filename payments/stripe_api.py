from typing_extensions import Literal

import stripe
from stripe.checkout import Session

from django.conf import settings
from django.db import transaction
from django.shortcuts import reverse

from payments.models import Payment
from borrowings.models import Borrowing

stripe.api_key = settings.STRIPE_API_KEY


class StripeSessionHandler:
    def __init__(
        self,
        borrowing: Borrowing,
        payment_type: Literal["PAYMENT", "FINE"] = "PAYMENT"
    ):
        self.borrowing = borrowing
        self.payment_type = payment_type

    def _get_price(self) -> int:
        if self.payment_type == "FINE":
            return int(self.borrowing.fee_price() * 100)
        else:
            return int(self.borrowing.price_for_borrowing() * 100)

    def _get_message(self) -> str:
        if self.payment_type == "FINE":
            return ("You are paying for overdue borrowing days"
                    f" - {self.borrowing.num_of_overdue_days()}")
        else:
            return ("You are paying for borrowing time of book "
                    f"{self.borrowing.book.title} - "
                    f"{self.borrowing.book.author}")

    @transaction.atomic
    def create_checkout_session(self, request, payment: Payment = None) -> str:
        """
        Create new Payment and Stripe Session to it but if
        payment parameter was provided then create new Stripe
        Session for current payment and return session url
        """
        book = self.borrowing.book
        price = self._get_price()

        if not isinstance(payment, Payment):
            payment = Payment.objects.create(
                status="PENDING",
                type=self.payment_type,
                borrowing=self.borrowing,
                money_to_pay=price,
            )
        payment = payment

        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "unit_amount": price,
                        "product_data": {
                            "name": f"{book.author} - {book.title}"
                        },
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url=request.build_absolute_uri(
                reverse("payments:payment-success", args=[payment.id])
            ),
            cancel_url=request.build_absolute_uri(
                reverse("payments:payment-cancel", args=[payment.id])
            ),
            custom_text={"submit": {"message": self._get_message()}},
        )

        payment.session_id = checkout_session.id
        payment.session_url = checkout_session.url
        payment.save()

        return checkout_session.url

    @staticmethod
    def get_checkout_session(session_id: str) -> Session:
        """Return Stripe Checkout Session"""
        return stripe.checkout.Session.retrieve(session_id)

    @staticmethod
    def session_is_expired(payment: Payment) -> bool:
        """
        If session is expired then update Payment status to
        EXPIRED and return True either False
        """
        session = StripeSessionHandler.get_checkout_session(payment.session_id)
        if session["status"] == "expired":
            payment.status = "EXPIRED"
            payment.save()
            return True
        return False
