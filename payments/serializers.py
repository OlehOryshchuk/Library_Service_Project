from rest_framework.serializers import ModelSerializer
from borrowings.serializers import BorrowingDetailSerializer

from .models import Payment


class PaymentListSerializer(ModelSerializer):
    borrowing = BorrowingDetailSerializer(read_only=True)

    class Model:
        model = Payment
        fields = [
            "id",
            "status",
            "borrowing",
        ]


class PaymentDetailSerializer(ModelSerializer):
    borrowing = BorrowingDetailSerializer(read_only=True)

    class Model:
        model = Payment
        fields = [
            "id",
            "status",
            "borrowing",
            "money_to_pay",
            "session_url",
        ]
