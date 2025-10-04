from core.thread_locals import get_current_tenant
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated
from rest_framework.response import Response

from .models import Order
from apps.users.roles import Role, get_role_group
from .serializers import OrderCreateSerializer, OrderReadSerializer
from .services import create_order_service, retry_order_service


class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, DjangoModelPermissions]  # noqa: RUF012
    queryset = Order.objects.all()

    def get_serializer_class(self):  # pyright: ignore[reportIncompatibleMethodOverride]  # noqa: ANN201
        if self.action == "create" or self.action == "bulk_create":
            return OrderCreateSerializer
        return OrderReadSerializer

    def get_queryset(self):  # noqa: ANN201
        """Filter queryset based on user's role."""
        user = self.request.user
        qs = super().get_queryset().select_related("product", "created_by__user")

        if user.is_superuser:
            return qs

        if user.profile.role == get_role_group(role=Role.OPERATOR):
            return qs.filter(created_by=user.profile)

        return qs.filter(company=user.profile.company)

    def perform_create(self, serializer) -> None:  # noqa: ANN001
        """Override to use the create_order_service."""
        company = get_current_tenant()
        create_order_service(
            product=serializer.validated_data["product"],
            quantity=serializer.validated_data["quantity"],
            created_by=self.request.user.profile,  # pyright: ignore[reportAttributeAccessIssue]
            company=company,
        )

    @action(detail=False, methods=["post"], url_path="bulk-create")
    def bulk_create(self, request):  # noqa: ANN001, ANN201
        """Endpoint for POST /api/orders/bulk-create/"""
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)

        for order_data in serializer.validated_data:
            company = get_current_tenant()
            create_order_service(
                product=order_data["product"],
                quantity=order_data["quantity"],
                created_by=request.user.profile,
                company=company,
            )
        return Response(
            {"status": "bulk order creation started"},
            status=status.HTTP_202_ACCEPTED,
        )

    @action(detail=True, methods=["post"])
    def retry(self, request, pk=None):  # noqa: ANN001, ANN201, ARG002
        """Endpoint for POST /api/orders/<id>/retry/"""
        order = self.get_object()
        try:
            retry_order_service(order=order)
            return Response({"status": "order re-queued for processing"})
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
