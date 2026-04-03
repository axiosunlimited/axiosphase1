from __future__ import annotations

from django.db import models
from django.conf import settings


class SystemSetting(models.Model):
    """Key/value system settings, stored as JSON.

    Used for configurable limits/toggles required by the HRIS requirements doc.
    """

    key = models.CharField(max_length=120, unique=True)
    value = models.JSONField(default=dict, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["key"]

    def __str__(self) -> str:
        return self.key

    @staticmethod
    def get_value(key: str, default=None):
        try:
            obj = SystemSetting.objects.filter(key=key).first()
            if obj is None:
                return default
            return obj.value
        except Exception:
            return default


class BackupArtifact(models.Model):
    """Logical record of a backup artifact stored in MEDIA_ROOT."""

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_backups",
    )
    file = models.FileField(upload_to="backups/")
    size_bytes = models.PositiveBigIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Backup {self.id} {self.created_at.isoformat()}"
