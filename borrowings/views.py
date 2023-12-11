from rest_framework import viewsets, mixins

from .models import Borrowing
from .serializers import (
    BorrowingDetailSerializer,
    BorrowingListSerializer,
    BorrowingCreateSerializer,
)


class BorrowingViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Borrowing.objects.select_related(
        "user", "book"
    )
    serializer_class = BorrowingListSerializer

    def get_serializer_class(self):
        self.serializer_class = {
            "list": BorrowingListSerializer,
            "retrieve": BorrowingDetailSerializer,
            "create": BorrowingCreateSerializer,
        }

        return self.serializer_class[self.action]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
