from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from apps.accounts.models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ("email", "username", "first_name", "last_name", "is_staff")
    ordering = ("email",)
    fieldsets = UserAdmin.fieldsets + (("Business", {"fields": ("phone", "company_name")}),)
    add_fieldsets = UserAdmin.add_fieldsets + (("Business", {"fields": ("phone", "company_name", "email")}),)
