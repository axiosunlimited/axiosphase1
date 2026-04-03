from __future__ import annotations

from celery import shared_task
from django.utils import timezone
from datetime import timedelta

from audit.models import AuditLog

from .utils import create_backup, get_setting_int


@shared_task
def scheduled_backup_task():
    enabled = bool(get_setting_int("backup.enabled", 1))
    if not enabled:
        return {"enabled": False}
    obj = create_backup(created_by=None)
    return {"enabled": True, "backup_id": obj.id, "size": obj.size_bytes}


@shared_task
def purge_audit_logs_task():
    days = get_setting_int("retention.audit_days", 365)
    cutoff = timezone.now() - timedelta(days=days)
    qs = AuditLog.objects.filter(created_at__lt=cutoff)
    count = qs.count()
    qs.delete()
    return {"deleted": count, "cutoff": cutoff.isoformat(), "days": days}
