from rest_framework import serializers

from apps.products.models import Product

from .models import Order


class OrderCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new orders."""

    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta:
        model = Order
        fields = ["product", "quantity"]  # noqa: RUF012


class OrderReadSerializer(serializers.ModelSerializer):
    """Serializer for displaying order details."""

    product_name = serializers.CharField(source="product.name", read_only=True)
    created_by = serializers.CharField(
        source="created_by.user.username",
        read_only=True,
    )

    class Meta:
        model = Order
        fields = [  # noqa: RUF012
            "reference_code",
            "product_name",
            "quantity",
            "status",
            "created_by",
            "created_at",
        ]
