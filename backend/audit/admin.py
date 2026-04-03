from django.contrib import admin
from .models import AuditLog

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "actor", "action", "model", "object_id")
    search_fields = ("model", "object_id", "actor__email")
    list_filter = ("action", "model")
