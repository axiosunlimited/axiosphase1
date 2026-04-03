from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserInvite

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ("email",)
    list_display = ("email", "full_name", "role", "twofa_enabled", "is_staff", "is_active")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Profile", {"fields": ("first_name", "last_name", "role")}),
        ("2FA", {"fields": ("twofa_enabled", "twofa_secret")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Security", {"fields": ("failed_login_attempts", "locked_until")}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("email", "password1", "password2", "role", "is_staff", "is_superuser")}),
    )
    search_fields = ("email", "first_name", "last_name")
    filter_horizontal = ("groups", "user_permissions")


@admin.register(UserInvite)
class UserInviteAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "role", "status", "auto_activate", "created_at", "expires_at", "used_at", "created_by")
    search_fields = ("email", "user__email", "created_by__email")
    list_filter = ("role", "auto_activate")
    readonly_fields = ("token_hash", "created_at", "used_at")
