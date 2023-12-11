from rest_framework.serializers import ModelSerializer

from books.serializers import BookDetailSerializer
from .models import Borrowing


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
