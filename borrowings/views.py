from rest_framework import viewsets, mixins

from .models import Borrowing
from .serializers import (
    BorrowingDetailSerializer,
    BorrowingListSerializer
)


class BorrowingViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
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
        }

        return self.serializer_class[self.action]
