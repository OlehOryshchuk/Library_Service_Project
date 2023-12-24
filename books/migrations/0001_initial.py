# Generated by Django 5.0 on 2023-12-15 18:44

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Book",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=100, unique=True)),
                ("author", models.CharField(max_length=255)),
                (
                    "cover",
                    models.CharField(
                        blank=True,
                        choices=[("HARD", "Hardcover"), ("SOFT", "Softcover")],
                        max_length=10,
                    ),
                ),
                ("inventory", models.PositiveIntegerField()),
                ("daily_fee", models.DecimalField(decimal_places=2, max_digits=20)),
            ],
            options={
                "indexes": [
                    models.Index(fields=["title"], name="books_book_title_d3218d_idx"),
                    models.Index(
                        fields=["author"], name="books_book_author_b941fe_idx"
                    ),
                ],
            },
        ),
    ]
