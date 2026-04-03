import hashlib
import secrets
from datetime import timedelta
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from audit.models import AuditLog
from .models import UserInvite

def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()

def _build_activation_link(token: str) -> str:
    base = getattr(settings, "FRONTEND_BASE_URL", "").rstrip("/")
    path = getattr(settings, "INVITE_ACCEPT_PATH", "/accept-invite")
    if not path.startswith("/"):
        path = "/" + path
    return f"{base}{path}?token={token}" if base else f"{path}?token={token}"

def create_and_send_invite(user, creator, expires_in_days=None, auto_activate=False):
    """
    Creates a UserInvite and sends an invitation email.
    """
    if expires_in_days is None:
        expires_in_days = getattr(settings, "INVITE_EXPIRE_DAYS", 7)
    
    now = timezone.now()
    # Expire any previous pending invites for this user
    UserInvite.objects.filter(user=user, used_at__isnull=True, expires_at__gt=now).update(expires_at=now)

    token = secrets.token_urlsafe(32)
    invite = UserInvite.objects.create(
        user=user,
        email=user.email,
        role=user.role,
        auto_activate=auto_activate,
        token_hash=_hash_token(token),
        created_by=creator,
        expires_at=now + timedelta(days=int(expires_in_days)),
    )

    activation_link = _build_activation_link(token)

    email_error = None
    subject = "You have been invited to HRIS"
    message = (
        f"Hello {user.full_name},\n\n"
        "An account has been created for you. "
        "Use the link below to set your password and activate your account:\n\n"
        f"{activation_link}\n\n"
        f"This invite expires on {invite.expires_at.isoformat()}.\n"
    )
    try:
        from notifications.tasks import send_async_email
        send_async_email.delay(
            subject=subject,
            message=message,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
            recipient_list=[user.email],
            fail_silently=False,
        )
        email_sent = True
    except Exception as e:
        email_sent = False
        email_error = e.__class__.__name__

    AuditLog.objects.create(
        actor=creator,
        action="CREATE",
        model="UserInvite",
        object_id=str(invite.pk),
        changes={
            "email": user.email,
            "role": user.role,
            "auto_activate": auto_activate,
            "expires_at": invite.expires_at.isoformat(),
            "email_sent": email_sent,
            "email_error": email_error,
            "info": "Invite created via utility (likely import or manual invite)"
        },
    )
    
    return {
        "invite": invite,
        "token": token,
        "activation_link": activation_link,
        "email_sent": email_sent,
        "email_error": email_error
    }
