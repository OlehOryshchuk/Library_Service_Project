from rest_framework.serializers import (
    ModelSerializer,
    ValidationError,
)
from rest_framework import serializers

from django.db import transaction
from django.core.exceptions import ValidationError

from books.serializers import BookDetailSerializer
from .models import Borrowing


class BorrowingCreateSerializer(ModelSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

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
    is_overdue = serializers.BooleanField()
    price_for_borrowing = serializers.SerializerMethodField()
    fee_price = serializers.SerializerMethodField()

    class Meta:
        model = Borrowing
        fields = [
            "id",
            "book",
            "is_overdue",
            "price_for_borrowing",
            "fee_price",
        ]

    def get_price_for_borrowing(self, borrowing: Borrowing):
        return borrowing.price_for_borrowing()

    def get_fee_price(self, borrowing: Borrowing):
        return borrowing.fee_price()


class BorrowingDetailSerializer(BorrowingListSerializer):
    num_of_borrowing_days = serializers.SerializerMethodField()
    num_of_overdue_days = serializers.SerializerMethodField()
    payment_session_link = serializers.SerializerMethodField()
    fine_payment_link = serializers.SerializerMethodField()

    class Meta(BorrowingListSerializer.Meta):
        fields = BorrowingListSerializer.Meta.fields + [
            "num_of_borrowing_days",
            "num_of_overdue_days",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "payment_session_link",
            "fine_payment_link",
        ]

    def get_num_of_borrowing_days(self, borrowing: Borrowing):
        return borrowing.num_of_borrowing_days()

    def get_num_of_overdue_days(self, borrowing: Borrowing):
        return borrowing.num_of_overdue_days()

    def get_payment_session_link(self, borrowing: Borrowing):
        return borrowing.payments.filter(type="PAYMENT").first().session_url

    def get_fine_payment_link(self, borrowing: Borrowing):
        fine_payment = borrowing.payments.filter(
            type="FINE"
        )
        if fine_payment.exists():
            return fine_payment.first()
        return None
