from __future__ import annotations

from typing import Any, Dict, Optional

from django.conf import settings
from django.core.mail import send_mail
from django.template import Template, Context

from .models import Notification, NotificationSetting, EmailTemplate


def _get_setting(key: str) -> NotificationSetting:
    obj = NotificationSetting.objects.filter(key=key).first()
    if obj:
        return obj
    return NotificationSetting.objects.create(key=key, enabled=True, config={"channels": ["in_app", "email"]})


def _get_template(key: str) -> EmailTemplate:
    obj = EmailTemplate.objects.filter(key=key).first()
    if obj:
        return obj
    # default placeholders
    return EmailTemplate.objects.create(
        key=key,
        enabled=True,
        subject_template=f"HRIS Notification: {key}",
        body_template="{{ message }}",
    )


def render_text(tpl: str, context: Dict[str, Any]) -> str:
    try:
        return Template(tpl).render(Context(context)).strip()
    except Exception:
        # fallback: best-effort
        return str(tpl)


def send_email_message(to_email: str, subject: str, body: str):
    if not to_email:
        return
    try:
        from .tasks import send_async_email
        from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None) or "no-reply@example.com"
        send_async_email.delay(
            subject=subject,
            message=body,
            from_email=from_email,
            recipient_list=[to_email],
            fail_silently=True
        )
    except Exception:
        # do not raise in background tasks
        pass


def notify_user(user, key: str, context: Optional[Dict[str, Any]] = None, title: str | None = None, message: str | None = None, email: bool = True, in_app: bool = True):
    """Create in-app notification and/or send email using configurable template."""
    context = context or {}
    setting = _get_setting(key)
    if not setting.enabled:
        return {"enabled": False}

    channels = setting.config.get("channels") if isinstance(setting.config, dict) else None
    if isinstance(channels, list):
        in_app = in_app and ("in_app" in channels)
        email = email and ("email" in channels)

    if title is None:
        title = context.get("title") or key.replace("_", " ").title()
    if message is None:
        message = context.get("message") or ""

    if in_app:
        Notification.objects.create(user=user, title=str(title)[:120], message=str(message))

    if email:
        tpl = _get_template(key)
        if tpl.enabled:
            subj = render_text(tpl.subject_template or "", {**context, "user": user, "title": title, "message": message})
            body = render_text(tpl.body_template or "", {**context, "user": user, "title": title, "message": message})
            send_email_message(getattr(user, "email", ""), subj, body)

    return {"enabled": True, "channels": {"in_app": in_app, "email": email}}
