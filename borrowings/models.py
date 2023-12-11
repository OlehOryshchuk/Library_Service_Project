from datetime import date

from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from books.models import Book


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(
        blank=True, null=True
    )
    book = models.ForeignKey(
        Book,
        related_name="borrowings",
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        get_user_model(),
        related_name="borrowings",
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f"{self.user} borrowed {self.book.title}"

    @staticmethod
    def check_date(date_value: date, error_key: str, error):
        if date_value < date.today():
            raise error({f"{error_key}": "Invalid date. Date in the past"})

    @staticmethod
    def validate_dates(actual_return_date: date, expected_return_date: date, error):
        Borrowing.check_date(actual_return_date, "actual_return_date", error)
        Borrowing.check_date(expected_return_date, "expected_return_date", error)

    def clean(self):
        Borrowing.validate_dates(
            self.actual_return_date,
            self.expected_return_date,
            ValidationError
        )

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        self.full_clean()
        return super().save(
            force_insert, force_update, using, update_fields
        )
