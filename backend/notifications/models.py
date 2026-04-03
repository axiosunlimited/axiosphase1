from __future__ import annotations

from django.db import models
from django.conf import settings


class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    title = models.CharField(max_length=120)
    message = models.TextField(blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class Feedback(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="feedback_items")
    category = models.CharField(max_length=60, default="GENERAL")
    message = models.TextField()
    page = models.CharField(max_length=120, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class NotificationSetting(models.Model):
    """Toggles + configuration for notification types."""

    key = models.CharField(max_length=120, unique=True)
    enabled = models.BooleanField(default=True)
    config = models.JSONField(default=dict, blank=True)  # lead times, channels, etc.
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["key"]

    def __str__(self):
        return self.key


class SystemAlert(models.Model):
    """System-generated alerts (contract expiry, probation, retirement, missing docs, etc.)."""

    class AlertType(models.TextChoices):
        CONTRACT_EXPIRY = "CONTRACT_EXPIRY", "Contract Expiry"
        PROBATION_END = "PROBATION_END", "Probation End"
        RETIREMENT = "RETIREMENT", "Retirement"
        MISSING_DOCUMENT = "MISSING_DOCUMENT", "Missing Document"
        LEAVE_BALANCE_LOW = "LEAVE_BALANCE_LOW", "Leave Balance Low"
        OTHER = "OTHER", "Other"

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        ACKNOWLEDGED = "ACKNOWLEDGED", "Acknowledged"
        RESOLVED = "RESOLVED", "Resolved"
        DISMISSED = "DISMISSED", "Dismissed"

    alert_type = models.CharField(max_length=40, choices=AlertType.choices)
    title = models.CharField(max_length=200)
    message = models.TextField(blank=True)
    employee = models.ForeignKey(
        "employees.Employee", null=True, blank=True,
        on_delete=models.CASCADE, related_name="system_alerts",
    )
    target_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.CASCADE, related_name="system_alerts",
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    metadata = models.JSONField(default=dict, blank=True)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="resolved_alerts",
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.alert_type}] {self.title}"


class EmailTemplate(models.Model):
    """Configurable email templates (subject/body) for notification events."""

    key = models.CharField(max_length=120, unique=True)
    enabled = models.BooleanField(default=True)
    subject_template = models.CharField(max_length=200, default="")
    body_template = models.TextField(default="")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["key"]

    def __str__(self):
        return self.key
