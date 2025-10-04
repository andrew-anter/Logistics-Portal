from core.thread_locals import get_current_tenant
from django import forms

from .models import Product
from .services import ProductData, create_product_service, update_product_service


class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ("name", "sku", "stock_quantity", "company", "is_active")

    def save(self, commit=True, request=None):  # noqa: ANN001, ANN201, ARG002, FBT002
        super().save(commit=False)
        product_data: ProductData = {
            "name": self.cleaned_data["name"],
            "is_active": self.cleaned_data["is_active"],
            "stock_quantity": self.cleaned_data["stock_quantity"],
        }

        if not self.instance.pk:
            if "company" not in self.cleaned_data:
                company = get_current_tenant()
            else:
                company = self.cleaned_data.get("company")

            if not company:
                msg = "Could not determine the company for the product."
                raise forms.ValidationError(msg)

            self.instance = create_product_service(company=company, **product_data)
        else:
            self.instance = update_product_service(
                product=self.instance,
                **product_data,
            )

        return self.instance
