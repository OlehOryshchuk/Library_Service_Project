from datetime import timedelta

from django.utils import timezone
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from books.models import Book


def overdue_day():
    return timezone.now().date() + timedelta(days=1)


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(blank=True, null=True)
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

    @property
    def is_overdue(self) -> bool:
        # check if borrowing was returned
        if self.actual_return_date is None:
            return self.expected_return_date < timezone.now().today().date()
        return False

    def num_of_borrowing_days(self) -> int:
        """Return number of usual borrowing days"""
        days = (self.expected_return_date - self.borrow_date).days
        # ensure a minimum of one day considered
        return max(days, 1)

    def num_of_overdue_days(self) -> int:
        """Return number of overdue days"""
        if self.is_overdue:
            return (overdue_day() - self.expected_return_date).days
        return 0

    def price_for_borrowing(self):
        """Return price for borrowing book"""
        return self.num_of_borrowing_days() * self.book.daily_fee

    def fee_price(self) -> int:
        """Return price for overdue days"""
        if self.is_overdue:
            return (
                self.num_of_overdue_days() * self.book.daily_fee
            ) * settings.FINE_MULTIPLIER
        return 0

    def validate_expected_return_date(self, error):
        if self.is_overdue:
            raise error(
                {"expected_return_date": "Invalid date. Date in the past"}
            )

    def clean(self):
        self.validate_expected_return_date(ValidationError)

    def save(
        self,
            force_insert=False,
            force_update=False,
            using=None,
            update_fields=None
    ):
        self.full_clean()
        return super().save(force_insert, force_update, using, update_fields)
