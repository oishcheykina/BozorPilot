from django.urls import path

from apps.accounts.views import UserLoginView, UserLogoutView, forgot_password, register, role_setup

app_name = "accounts"

urlpatterns = [
    path("login/", UserLoginView.as_view(), name="login"),
    path("register/", register, name="register"),
    path("logout/", UserLogoutView.as_view(), name="logout"),
    path("setup/", role_setup, name="role_setup"),
    path("forgot-password/", forgot_password, name="forgot_password"),
]
