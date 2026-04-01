from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from apps.accounts.models import User


class LoginForm(AuthenticationForm):
    username = forms.EmailField(label="Email")


class RegisterForm(UserCreationForm):
    ROLE_CHOICES = (("consumer", "Consumer"), ("business", "Business"))

    email = forms.EmailField()
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    company_name = forms.CharField(max_length=255, required=False)
    role = forms.ChoiceField(choices=ROLE_CHOICES)

    class Meta:
        model = User
        fields = ("email", "username", "first_name", "last_name", "company_name", "role", "password1", "password2")

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get("role")
        company_name = (cleaned_data.get("company_name") or "").strip()
        if role == "business" and not company_name:
            self.add_error("company_name", "Business account uchun company name majburiy.")
        return cleaned_data


class ProfileForm(forms.Form):
    preferred_language = forms.ChoiceField(choices=(("uz", "Uzbek"), ("ru", "Russian"), ("en", "English")))
    location = forms.CharField(max_length=120, required=False)
    company_type = forms.CharField(max_length=120, required=False)

    def __init__(self, *args, role_code=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.role_code = role_code
        if role_code != "business":
            self.fields["company_type"].required = False

    def clean(self):
        cleaned_data = super().clean()
        company_type = (cleaned_data.get("company_type") or "").strip()
        if self.role_code == "business" and not company_type:
            self.add_error("company_type", "Business account uchun company type majburiy.")
        return cleaned_data
