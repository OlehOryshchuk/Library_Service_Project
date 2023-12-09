from rest_framework import viewsets
from rest_framework.permissions import (
    AllowAny,
    IsAdminUser,
    IsAuthenticated
)

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

    def get_permissions(self):
        if self.action in [
            "update",
            "create",
            "partial_update",
            "delete",
        ]:
            self.permission_classes = [IsAdminUser]

        elif self.action == "list":
            self.permission_classes = [AllowAny]

        elif self.action == "detail":
            self.permission_classes = [IsAuthenticated]

        return super().get_permissions()
