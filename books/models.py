from django.db import models


class Book(models.Model):
    class CoverType(models.TextChoices):
        HARD = "HARD", "Hardcover"
        SOFT = "SOFT", "Softcover"

    title = models.CharField(max_length=100, unique=True)
    author = models.CharField(max_length=255)
    cover = models.CharField(
        choices=CoverType.choices,
        max_length=10,
        blank=True
    )
    inventory = models.PositiveIntegerField()
    daily_fee = models.DecimalField(decimal_places=4, max_digits=20)

    class Meta:
        indexes = [
            models.Index(fields=["title"]),
            models.Index(fields=["author"]),
        ]
