from rest_framework import serializers
from .models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    actor_email = serializers.CharField(source="actor.email", read_only=True)
    actor_role = serializers.CharField(source="actor.role", read_only=True)

    class Meta:
        model = AuditLog
        fields = [
            "id",
            "created_at",
            "actor",
            "actor_email",
            "actor_role",
            "action",
            "model",
            "object_id",
            "changes",
        ]
        read_only_fields = fields
