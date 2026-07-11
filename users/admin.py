from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User

    # какие поля показывать в списке
    list_display = (
        "email",
        "full_name",
        "position",
        "role",
        "is_active_employee",
        "is_staff",
        "is_superuser",
    )
    list_filter = ("role", "is_active_employee", "is_staff", "is_superuser")
    search_fields = ("email", "full_name", "position")

    # поля для редактирования
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("full_name", "position", "role", "is_active_employee")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "full_name",
                    "position",
                    "role",
                    "password1",
                    "password2",
                ),
            },
        ),
    )

    ordering = ("email",)
