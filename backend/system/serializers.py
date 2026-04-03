from rest_framework import serializers
from .models import SystemSetting, BackupArtifact


class SystemSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemSetting
        fields = ["id", "key", "value", "updated_at"]
        read_only_fields = ["updated_at"]


class BackupArtifactSerializer(serializers.ModelSerializer):
    class Meta:
        model = BackupArtifact
        fields = ["id", "file", "size_bytes", "created_at", "created_by"]
        read_only_fields = ["size_bytes", "created_at", "created_by"]
