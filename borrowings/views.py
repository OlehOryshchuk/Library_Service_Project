from django.utils import timezone
from django.db import transaction
from django.db.models import Subquery, OuterRef, QuerySet
from django.shortcuts import redirect

from rest_framework.response import Response
from rest_framework import (
    viewsets,
    mixins,
    status,
)
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample

from .models import Borrowing
from .serializers import (
    BorrowingDetailSerializer,
    BorrowingListSerializer,
    BorrowingCreateSerializer,
)
from payments.stripe_api import (
    StripeSessionHandler,
)
from payments.models import Payment


class BorrowingViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Borrowing.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = BorrowingListSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["book__title", "book__author"]
    ordering_fields = ["borrow_date", "actual_return_date"]

    def queryset_enhancement(self, queryset: QuerySet):
        """
        Subquery is a way to include the result of a subquery
        to main query 'queryset'
        so for each borrowing we get it's payment and fine status
        which we would later use in BorrowingListSerializer
        """
        borrowing_payment_subquery = Payment.objects.filter(
            borrowing=OuterRef("pk"), type="PAYMENT"
        ).values("status")
        borrowing_fine_subquery = Payment.objects.filter(
            borrowing=OuterRef("pk"), type="FINE"
        ).values("status")
        queryset = queryset.select_related(
            "book", "user"
        ).annotate(
            payment_status=Subquery(borrowing_payment_subquery),
            fine_status=Subquery(borrowing_fine_subquery),
        )

        return queryset

    def get_queryset(self):
        user = self.request.user
        queryset = (
            Borrowing.objects.all()
            if user.is_staff
            else Borrowing.objects.filter(user=user)
        )
        queryset = self.queryset_enhancement(queryset)
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
            "renew_payment": BorrowingDetailSerializer,
            "create": BorrowingCreateSerializer,
        }

        return self.serializer_class.get(self.action)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="search",
                description=(
                        "Search borrowings by book title or author"
                        " ?search=title/author"
                ),
                type=str,
                required=False,
            ),
            OpenApiParameter(
                name="ordering",
                description=(
                        "Order borrowings by borrow date or actual return date"
                        " ?ordering=borrow_date/actual_return_date"
                ),
                type=str,
                required=False,
                examples=[
                    OpenApiExample(
                        "Example2",
                        description="Order by borrow date",
                        value="borrow_date",
                    ),
                    OpenApiExample(
                        "Example3",
                        description="Order by actual return date",
                        value="actual_return_date",
                    ),
                ],
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        borrowing_data = super().create(request, *args, **kwargs).data
        borrowing = Borrowing.objects.get(id=borrowing_data["id"])
        # if user have at least 1 unpaid payment then
        # forbid to create new borrowing
        pending_payments = borrowing.payments.filter(status="PENDING")
        if pending_payments.exists():
            return Response(
                {"pending_payments_error": "User have unpaid payments, paid fist"},
                status=status.HTTP_400_BAD_REQUEST
            )

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
        methods=["get"],
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

        serializer = self.get_serializer(borrowing)
        return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)

