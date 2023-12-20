from rest_framework import serializers

from django.utils import timezone

from borrowings.serializers import BorrowingDetailSerializer

from .models import Payment


class PaymentListSerializer(serializers.ModelSerializer):
    borrowings = BorrowingDetailSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "status",
            "borrowings",
        ]


class PaymentDetailSerializer(serializers.ModelSerializer):
    borrowings = BorrowingDetailSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "status",
            "borrowings",
            "money_to_pay",
            "session_url",
        ]
