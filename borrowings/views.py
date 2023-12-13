from django.utils import timezone
from django.db import transaction

from rest_framework.response import Response
from rest_framework import (
    viewsets,
    mixins,
    status,
)
from rest_framework.decorators import action
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
    # permission_classes = [IsAuthenticated]
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

    @transaction.atomic
    @action(
        methods=["post"],
        detail=True,
        url_name="return",
        url_path="return"
    )
    def return_borrowing(self, request, pk):
        """
        User return book, increase book inventory +1,
        check if user has not return it twice,
        return updated borrowing
        """
        borrowing = self.get_object()

        if borrowing.actual_return_date is not None:
            message = {
                "borrowing": (
                    f"You have already return that book"
                )
            }
            return Response(message, status=status.HTTP_400_BAD_REQUEST)

        # increase inventory
        book = borrowing.book
        book.inventory += 1
        book.save()
        # set date when user has returned the book
        borrowing.actual_return_date = timezone.now().date()
        borrowing.save()

        serializer = BorrowingDetailSerializer(borrowing)
        return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
