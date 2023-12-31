from django.core.validators import URLValidator
from django.db import models


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "pending"
        PAID = "PAID", "paid"
        EXPIRED = "EXPIRED", "expired"

    class Type(models.TextChoices):
        PAYMENT = "PAYMENT ", "payment"
        FINE = "FINE", "fine"

    status = models.CharField(
        max_length=8,
        choices=Status.choices,
        blank=True,
    )
    type = models.CharField(
        max_length=8,
        choices=Type.choices,
        blank=True,
    )
    borrowing = models.ForeignKey(
        "borrowings.Borrowing",
        on_delete=models.CASCADE,
        related_name="payments",
    )
    session_url = models.TextField(validators=[URLValidator()] , max_length=2000)
    session_id = models.CharField(max_length=255, unique=True)
    money_to_pay = models.DecimalField(
        decimal_places=2,
        max_digits=20,
    )

    def __str__(self):
        return f"{self.borrowing}"
