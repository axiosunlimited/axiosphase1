from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver
from .models import AuditLog

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    AuditLog.objects.create(
        actor=user,
        action="LOGIN",
        model="User",
        object_id=str(user.pk),
        changes={"info": "User logged in"}
    )

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    if user:
        AuditLog.objects.create(
            actor=user,
            action="LOGOUT",
            model="User",
            object_id=str(user.pk),
            changes={"info": "User logged out"}
        )

@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    email = credentials.get("email") or credentials.get("username") or "unknown"
    AuditLog.objects.create(
        actor=None,
        action="LOGIN_FAILED",
        model="User",
        object_id="0",
        changes={"email": email, "info": "Failed login attempt"}
    )
