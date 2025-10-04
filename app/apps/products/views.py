from django.db.models import QuerySet
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import Product
from .serializers import ProductSerializer


class ProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    # Protect the endpoint, only authenticated users can access it
    permission_classes = [IsAuthenticated]  # noqa: RUF012

    def get_queryset(self) -> QuerySet[Product]:  # pyright: ignore[reportIncompatibleMethodOverride]
        """
        This view should return a list of all the products
        for the currently authenticated user's company.
        """
        user = self.request.user
        return Product.objects.filter(company=user.profile.company)  # pyright: ignore[reportAttributeAccessIssue]
