from rest_framework.serializers import ModelSerializer

from .models import Book


class BookSerializer(ModelSerializer):
    class Meta:
        model = Book
        fields = "__all__"


class BookListSerializer(ModelSerializer):
    class Meta:
        model = Book
        fields = ["title", "author", "inventory"]


class BookDetailSerializer(ModelSerializer):
    class Meta:
        model = Book
        fields = "__all__"
