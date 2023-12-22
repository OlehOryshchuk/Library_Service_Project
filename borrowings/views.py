from django.utils import timezone
from django.db import transaction
from django.shortcuts import redirect

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
from payments.stripe_api import (
    StripeSessionHandler,
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

        return self.serializer_class.get(self.action)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        borrowing_data = super().create(request, *args, **kwargs).data

        borrowing = Borrowing.objects.get(id=borrowing_data["id"])
        session_creator = StripeSessionHandler(
            borrowing=borrowing,
            payment_type="PAYMENT"
        )
        return redirect(session_creator.create_checkout_session(request))

    @action(detail=True, methods=["get"])
    def renew_payment(self, request, *args, **kwargs):
        """
        Check if borrowing payment is expired if yes then
        create new Stripe Session for borrowing
        """
        borrowing = self.get_object()
        # borrowing can have only 2 Payment relation
        # with "FINE" and "PYMENT" type so
        # we will update both Session of FINE and PYMENT type
        payments = borrowing.payments.filter(status="EXPIRED")
        for payment in payments:
            session_creator = StripeSessionHandler(borrowing, payment.type)
            # pass payment to create_checkout_session, it will
            # update session_url and session_d
            session_creator.create_checkout_session(payment)
        return Response(status=status.HTTP_200_OK)

    @transaction.atomic
    @action(
        methods=["post"],
        detail=True,
        url_name="return",
        url_path="return"
    )
    def return_borrowing(self, request, pk):
        """
        User returns book, increase book inventory +1,
        check if user has not return it twice and  return updated borrowing.
        If borrowing is overdue than redirect to Payment session
        to pay fines.
        """
        borrowing = self.get_object()

        if borrowing.is_overdue:
            # Create Payment Session for paying fees for overdue
            session_creator = StripeSessionHandler(
                borrowing=borrowing,
                payment_type="FINE"
            )
            return redirect(
                session_creator.create_checkout_session(request)
            )

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

