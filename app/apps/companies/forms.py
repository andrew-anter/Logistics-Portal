from django import forms

from .models import Company
from .services import create_company


class CompanyAdminForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ("name", "domain", "is_active")

    def save(self, commit=True):
        instance = super().save(commit=False)

        if not instance.pk:
            instance = create_company(
                name=instance.name,
                domain=instance.domain,
                is_active=instance.is_active,
            )

        if commit:
            instance.save()
            self.save_m2m()

        return instance
