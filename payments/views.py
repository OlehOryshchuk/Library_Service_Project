from stripe.checkout import Session

from django.utils.timezone import datetime
from django.utils import timezone

from rest_framework import (
    viewsets,
    mixins,
    status,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample

from .serializers import (
    PaymentDetailSerializer,
    PaymentListSerializer,
)
from .models import Payment
from .stripe_api import (
    StripeSessionHandler,
)
from .success_payment_nofication import (
    send_success_payment_notification
)


class PaymentViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Payment.objects.all()
    serializer_class = PaymentListSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["status", "type"]

    def get_queryset(self):
        user = self.request.user
        queryset = (
            self.queryset
            if user.is_staff
            else Payment.objects.filter(borrowing__user=user)
        )

        return queryset.select_related(
            "borrowing__user", "borrowing__book"
        ).prefetch_related()

    def get_serializer_class(self):
        self.serializer_class = {
            "list": PaymentListSerializer,
            "retrieve": PaymentDetailSerializer,
        }
        return self.serializer_class[self.action]

    def _message(self, checkout_session: Session) -> dict:
        # expire date which expressed in Unix timestamp
        expire_date_seconds = checkout_session.get("expires_at")
        # convert to Coordinated Universal Time (UTC)
        expire_date_utc = datetime.utcfromtimestamp(expire_date_seconds)
        # convert to local date
        expire_date_local = expire_date_utc.astimezone(
            timezone.get_current_timezone()
        )
        formatted_expire_date = expire_date_local.strftime("%Y-%m-%d %H:%M:%S %Z")

        return {
            "expire_date": formatted_expire_date,
            "payment_status": checkout_session.get("payment_status"),
            "currency": checkout_session.get("currency"),
            "total_price": checkout_session.get("amount_total") / 100
        }

    @action(detail=True, methods=["get"])
    def success(self, request, *args, **kwargs):
        """
        if payment was paid update Payment status
        ot not.
        """
        payment = self.get_object()
        checkout_session = StripeSessionHandler.get_checkout_session(
            payment.session_id
        )
        # check if payment is already paid then there is no
        # need to update and send telegram notification
        if checkout_session.get("payment_status") == "paid" and payment.status != "PAID":
            payment.status = "PAID"
            payment.save()
            send_success_payment_notification(payment.borrowing)
            return Response(
                self._message(checkout_session),
                status=status.HTTP_204_NO_CONTENT
            )
        return Response(
            self._message(checkout_session),
            status=status.HTTP_204_NO_CONTENT
        )

    @action(detail=True, methods=["get"])
    def cancel(self, request, *args, **kwargs):
        """
        Just inform user about payment can be paid later
        """
        payment = self.get_object()
        checkout_session = StripeSessionHandler.get_checkout_session(
            payment.session_id
        )
        message = self._message(checkout_session)
        message.update({
                "info": (
                    "Payment can be paid a bit later "
                    "(but the session is available for only 24h)"
                )
        })
        return Response(
            message,
            status=status.HTTP_204_NO_CONTENT
        )
