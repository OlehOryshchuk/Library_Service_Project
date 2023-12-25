from datetime import date, timedelta

from django.contrib.auth import get_user_model

from borrowings.models import Borrowing
from books.models import Book

from payments.stripe_api import StripeSessionHandler


def borrowing_sample(book: Book, user: get_user_model, request, **param):
    """Function for tests, return borrowing instance"""
    default = {
        "expected_return_date":  date.today() + timedelta(days=4),
        "actual_return_date": None,
        "book": book,
        "user": user,
    }
    # Borrowing list, detail endpoints use some fields
    # from borrowing payment, so we need to create payment

    default.update(**param)

    borrowing = Borrowing.objects.create(**default)
    stripe_session = StripeSessionHandler(borrowing)
    stripe_session.create_checkout_session(request=request)

    return borrowing
