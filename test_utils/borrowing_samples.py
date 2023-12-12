from datetime import date, timedelta

from django.contrib.auth import get_user_model

from borrowings.models import Borrowing
from books.models import Book


def borrowing_sample(book: Book, user: get_user_model, **param):
    """Function for tests, return borrowing instance"""
    default = {
        "expected_return_date":  date.today() + timedelta(days=4),
        "actual_return_date": None,
        "book": book,
        "user": user,
    }
    default.update(**param)

    return Borrowing.objects.create(**default)
