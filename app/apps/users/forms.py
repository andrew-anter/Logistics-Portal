from core.thread_locals import get_current_tenant
from django import forms
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError as CoreValidationError

from .models import Profile, User
from .services import create_profile_service, update_profile_service


class ProfileAdminForm(forms.ModelForm):
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

    def clean_email(self):  # noqa: ANN201
        """
        Check that the email is unique for the given company.
        """
        email = self.cleaned_data.get("email")
        company = self.cleaned_data.get("company")

        if company and email:
            query = User.objects.filter(profile__company=company, email__iexact=email)

            if self.instance and self.instance.pk:
                query = query.exclude(pk=self.instance.user.pk)

            if query.exists():
                msg = "A user with this email already exists in the system."
                raise forms.ValidationError(msg)

        return email

    def save(self, commit=True):  # noqa: ANN001, ANN201, FBT002
        if "company" not in self.cleaned_data:
            company = get_current_tenant()
        else:
            company = self.cleaned_data["company"]
        if not self.instance.pk:
            profile = create_profile_service(
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
            update_profile_service(profile=profile, **self.cleaned_data)

            if commit:
                super().save(commit=False)
                self.save_m2m()

        return self.instance
