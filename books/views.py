from rest_framework import viewsets

from .models import Book
from .serializers import (
    BookSerializer,
    BookListSerializer,
    BookDetailSerializer,
)


class BookViewSet(viewsets.ModelViewSet):
    serializer_class = BookSerializer
    queryset = Book.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return BookListSerializer

        elif self.action == "retrieve":
            return BookDetailSerializer

        return BookSerializer
