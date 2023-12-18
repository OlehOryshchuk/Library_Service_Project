from rest_framework import (
    viewsets,
    mixins,
)
from rest_framework.permissions import IsAuthenticated

from .serializers import (
    PaymentDetailSerializer,
    PaymentListSerializer,
    PaymentSerializer,
)
from .models import Payment


class PaymentViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Payment.objects.select_related(
        "borrowing__user", "borrowing__book"
    )
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = (
            self.queryset
            if user.is_staff
            else Payment.objects.filter(borrowings__user=user)
        )

        return queryset