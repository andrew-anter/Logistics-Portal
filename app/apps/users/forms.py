from core.thread_locals import get_current_tenant
from django import forms
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError as CoreValidationError

from .models import Profile
from .services import create_profile_service


class ProfileAdminForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    password = forms.CharField(
        widget=forms.PasswordInput(),
        required=False,
        help_text="Leave blank to keep the current password if the user is being modified.",  # noqa: E501
    )

    class Meta:
        model = Profile
        fields = ("company", "role", "is_blocked")

    def __init__(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.user:
            self.fields["username"].initial = self.instance.user.username
            self.fields["email"].initial = self.instance.user.email
            self.fields["first_name"].initial = self.instance.user.first_name
            self.fields["last_name"].initial = self.instance.user.last_name
        else:
            self.fields["password"].required = True

    def clean_password(self):  # noqa: ANN201
        password = self.cleaned_data.get("password")

        if not self.instance.pk or password:
            try:
                password_validation.validate_password(password=password)  # pyright: ignore[reportArgumentType]
            except CoreValidationError as e:
                raise forms.ValidationError(e.messages)  # pyright: ignore[reportArgumentType]

        return password

    def save(self, commit=True):  # noqa: ANN001, ANN201, FBT002
        if "company" not in self.cleaned_data:
            company = get_current_tenant()
        else:
            company = self.cleaned_data["company"]
        if not self.instance.pk:
            profile = create_profile_service(
                username=self.cleaned_data["username"],
                email=self.cleaned_data["email"],
                first_name=self.cleaned_data["first_name"],
                last_name=self.cleaned_data["last_name"],
                company=company,
                role=self.cleaned_data["role"],
                password=self.cleaned_data["password"],
            )
            self.instance = profile

        else:
            profile = super().save(commit=False)
            user = profile.user
            user.username = self.cleaned_data["username"]
            user.email = self.cleaned_data["email"]
            user.first_name = self.cleaned_data["first_name"]
            user.last_name = self.cleaned_data["last_name"]
            user.set_password(self.cleaned_data["password"])

            if commit:
                super().save(commit=False)
                user.save()
                profile.save()
                self.save_m2m()

        return self.instance
