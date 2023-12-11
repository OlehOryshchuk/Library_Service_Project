from rest_framework.serializers import ModelSerializer
from django.core.exceptions import ValidationError

from books.serializers import BookDetailSerializer
from .models import Borrowing


class BorrowingCreateSerializer(ModelSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        Borrowing.validate_dates(
            attrs["actual_return_date"],
            attrs["expected_return_date"],
            ValidationError
        )


    class Meta:
        model = Borrowing
        fields = [
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
        ]
        read_only_fields = ["borrow_date"]


class BorrowingListSerializer(ModelSerializer):
    book = BookDetailSerializer(read_only=True)

    class Meta:
        model = Borrowing
        fields = [
            "id",
            "book"
        ]


class BorrowingDetailSerializer(ModelSerializer):

    class Meta:
        model = Borrowing
        fields = "__all__"
