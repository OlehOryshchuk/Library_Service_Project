from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated

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
    queryset = Borrowing.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = BorrowingListSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = (
            Borrowing.objects.all()
            if user.is_staff
            else Borrowing.objects.filter(user=user)
        )
        is_active = self.request.query_params.get("is_active", None)
        user_id = self.request.query_params.get("user_id", None)

        # if is_active=True return active borrowings
        if is_active == "True":
            queryset = queryset.filter(
                actual_return_date__isnull=True
            )
        # if is_active=False return not active borrowings
        elif is_active == "False":
            queryset = queryset.filter(
                actual_return_date__isnull=False
            )

        if user.is_staff:
            if user_id:
                queryset = queryset.filter(user_id=int(user_id))

        return queryset

    def get_serializer_class(self):
        self.serializer_class = {
            "list": BorrowingListSerializer,
            "retrieve": BorrowingDetailSerializer,
            "create": BorrowingCreateSerializer,
        }

        return self.serializer_class[self.action]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
