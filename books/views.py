from rest_framework import viewsets
from rest_framework.permissions import (
    AllowAny,
    IsAdminUser,
    IsAuthenticated
)
from rest_framework.filters import SearchFilter, OrderingFilter

from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
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
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["title", "author"]
    ordering_fields = ["author"]

    def get_serializer_class(self):
        self.serializer_class = {
            "list": BookListSerializer,
            "retrieve": BookDetailSerializer,
        }

        return self.serializer_class.get(self.action, BookSerializer)

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

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="search",
                description="Search books by title or author, ?search=title/author",
                type=str,
                required=False,
            ),
            OpenApiParameter(
                name="ordering",
                description="Order books by author ?ordering=author",
                type=str,
                required=False,
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
