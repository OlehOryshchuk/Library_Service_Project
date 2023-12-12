from rest_framework.serializers import (
    ModelSerializer,
    ValidationError,
)

from django.db import transaction
from django.core.exceptions import ValidationError

from books.serializers import BookDetailSerializer
from .models import Borrowing


class BorrowingCreateSerializer(ModelSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        Borrowing.validate_expected_return_date(
            attrs["expected_return_date"],
            ValidationError
        )

        if attrs["book"].inventory < 1:
            raise ValidationError({"book": "Book is out of stock"})

        return data

    class Meta:
        model = Borrowing
        fields = [
            "id",
            "borrow_date",
            "expected_return_date",
            "book",
        ]
        read_only_fields = ["borrow_date"]

    @transaction.atomic
    def create(self, validated_data):
        book = validated_data["book"]
        book.inventory -= 1
        book.save()
        
        return super().create(validated_data)
        

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
        exclude = ["user"]
