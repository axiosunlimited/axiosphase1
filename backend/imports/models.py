from __future__ import annotations

from django.db import models
from django.conf import settings


class ImportJob(models.Model):
    class Kind(models.TextChoices):
        EMPLOYEES = "EMPLOYEES", "Employees"
        LEAVE_BALANCES = "LEAVE_BALANCES", "Leave balances"
        CONTRACTS = "CONTRACTS", "Contracts"

    class Status(models.TextChoices):
        UPLOADED = "UPLOADED", "Uploaded"
        PREVIEWED = "PREVIEWED", "Previewed"
        COMMITTED = "COMMITTED", "Committed"
        FAILED = "FAILED", "Failed"

    kind = models.CharField(max_length=40, choices=Kind.choices)
    upload = models.FileField(upload_to="imports/")
    mapping = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.UPLOADED)

    preview_rows = models.JSONField(default=list, blank=True)
    errors = models.JSONField(default=list, blank=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"ImportJob<{self.kind}> {self.id}"
