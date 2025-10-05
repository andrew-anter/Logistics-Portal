from django import forms

from .models import Order


class OrderAdminForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["product", "quantity"]  # noqa: RUF012
