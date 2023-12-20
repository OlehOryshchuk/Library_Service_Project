import stripe
from django.conf import settings
from django.db import transaction

from django.shortcuts import reverse
from payments.models import Payment
from borrowings.models import Borrowing


def borrowing_days(borrowing: Borrowing) -> int:
    """Return number of days the book will be borrowed"""
    return (
            borrowing.expected_return_date -
            borrowing.borrow_date
    ).days


def total_price(borrowing: Borrowing) -> int:
    """
    Calculate total price for borrowing
    """
    return borrowing_days(borrowing) * borrowing.book.daily_fee


def price_in_cents(borrowing: Borrowing) -> int:
    return int(total_price(borrowing=borrowing) * 100)


@transaction.atomic
def create_payment_session(borrowing: Borrowing, request) -> None:
    """
    Create Stripe Payment Checkout Session to pay for borrowing
    and create Payment record using Session.url and id
    finally return url to Stripe-hosted payment page.
    """
    stripe.api_key = settings.STRIPE_API_KEY

    book = borrowing.book
    payment = Payment.objects.create(
        status="PENDING",
        type="PAYMENT",
        borrowings=borrowing,
        money_to_pay=total_price(borrowing),
    )

    checkout_session = stripe.checkout.Session.create(
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "unit_amount": price_in_cents(borrowing),
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
            "submit": {"message": (
                "You will pay for borrowing time - "
                f"{borrowing_days(borrowing)} days"
            )
            }
        }
    )

    payment.session_id = checkout_session.id
    payment.session_url = checkout_session.url

    payment.save()

    return checkout_session.url
