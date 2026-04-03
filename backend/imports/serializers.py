from rest_framework import serializers
from .models import ImportJob


class ImportJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImportJob
        fields = [
            "id",
            "kind",
            "upload",
            "mapping",
            "status",
            "preview_rows",
            "errors",
            "created_by",
            "created_at",
        ]
        read_only_fields = ["status", "preview_rows", "errors", "created_by", "created_at"]
