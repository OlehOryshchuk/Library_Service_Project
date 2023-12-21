from typing_extensions import Literal

import stripe
from django.conf import settings
from django.db import transaction

from django.shortcuts import reverse
from payments.models import Payment
from borrowings.models import Borrowing


class StripeSessionCreator:
    def __init__(self, borrowing: Borrowing, payment_type: Literal["PAYMENT", "FINE"] = "PAYMENT"):
        self.borrowing = borrowing
        self.payment_type = payment_type

    def _get_price(self) -> int:
        if self.payment_type == "FINE":
            return int(self.borrowing.fee_price() * 100)
        else:
            return int(self.borrowing.price_for_borrowing() * 100)

    def _get_message(self) -> str:
        if self.payment_type == "FINE":
            return f"You are paying for overdue borrowing days - {self.borrowing.num_of_overdue_days()}"
        else:
            return f"You are paying for borrowing time of book {self.borrowing.book.title} - {self.borrowing.book.author}"

    @transaction.atomic
    def create_checkout_session(self, request) -> str:
        stripe.api_key = settings.STRIPE_API_KEY

        book = self.borrowing.book
        price = self._get_price()

        payment = Payment.objects.create(
            status="PENDING",
            type=self.payment_type,
            borrowings=self.borrowing,
            money_to_pay=price,
        )

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
            custom_text={
                "submit": {"message": self._get_message()}
            }
        )

        payment.session_id = checkout_session.id
        payment.session_url = checkout_session.url
        payment.save()

        return checkout_session.url
