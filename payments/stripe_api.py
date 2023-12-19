import stripe
from django.conf import settings
from django.db import transaction
from django.shortcuts import redirect

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
    :param self:
    :param borrowing:
    :return:
    """
    return borrowing_days(borrowing) * borrowing.book.daily_fee


def price_in_cents(borrowing: Borrowing) -> int:
    return int(total_price(borrowing=borrowing) * 100)


@transaction.atomic
def create_payment_session(borrowing: Borrowing) -> None:
    """
    Create Stripe Payment Checkout Session to pay for borrowing
    and create Payment record using Session.url and id
    finally return url to Stripe-hosted payment page.
    """
    stripe.api_key = settings.STRIPE_API_KEY
    domain = settings.DOMAIN_NAME

    book = borrowing.book

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
        success_url=f"{domain}api/borrowings/{borrowing.id}/",
        cancel_url=f"{domain}api/borrowings/{borrowing.id}/",
        custom_text={
            "submit": {"message": (
                "You will pay for borrowing time - "
                f"{borrowing_days(borrowing)} days"
            )
            }
        }
    )

    Payment.objects.create(
        status="PENDING",
        type="PAYMENT",
        borrowings=borrowing,
        session_url=checkout_session.url,
        session_id=checkout_session.id,
        money_to_pay=total_price(borrowing),
    )

    return checkout_session.url
