from rest_framework import serializers

from books.serializers import BookDetailSerializer

from .models import Payment


class PaymentListSerializer(serializers.ModelSerializer):
    borrowing_book = BookDetailSerializer(
        read_only=True,
        source="borrowing.book"
    )

    class Meta:
        model = Payment
        fields = [
            "id",
            "status",
            "type",
            "borrowing_book",
            "borrowing",
        ]


class PaymentDetailSerializer(serializers.ModelSerializer):
    borrowing_book = BookDetailSerializer(
        read_only=True,
        source="borrowing.book"
    )

    class Meta:
        model = Payment
        fields = [
            "id",
            "status",
            "type",
            "borrowing_book",
            "borrowing",
            "money_to_pay",
            "session_url",
        ]
