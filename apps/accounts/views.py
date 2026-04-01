from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render

from apps.accounts.forms import LoginForm, ProfileForm, RegisterForm
from apps.core.models import Profile, Role


class UserLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = LoginForm


class UserLogoutView(LogoutView):
    pass


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            role_code = form.cleaned_data.pop("role")
            user = form.save()
            role = Role.objects.filter(code=role_code).first()
            Profile.objects.update_or_create(user=user, defaults={"role": role})
            login(request, user)
            messages.success(request, "Akkaunt yaratildi. Profilni yakunlang.")
            return redirect("accounts:role_setup")
    else:
        form = RegisterForm()
    return render(request, "accounts/register.html", {"form": form})


@login_required
def role_setup(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    role_code = getattr(profile.role, "code", None)
    if request.method == "POST":
        form = ProfileForm(request.POST, role_code=role_code)
        if form.is_valid():
            profile.preferred_language = form.cleaned_data["preferred_language"]
            profile.location = form.cleaned_data["location"]
            profile.company_type = form.cleaned_data["company_type"]
            profile.onboarding_completed = True
            profile.save()
            messages.success(request, "Profil sozlandi.")
            return redirect("core:router")
    else:
        form = ProfileForm(
            initial={
                "preferred_language": profile.preferred_language,
                "location": profile.location,
                "company_type": profile.company_type,
            },
            role_code=role_code,
        )
    return render(request, "accounts/role_setup.html", {"form": form, "profile": profile})


def forgot_password(request):
    return render(request, "accounts/forgot_password.html")
