from rest_framework import serializers
from .models import ReportDefinition


class ReportDefinitionSerializer(serializers.ModelSerializer):
    created_by_email = serializers.CharField(source="created_by.email", read_only=True)

    class Meta:
        model = ReportDefinition
        fields = [
            "id",
            "name",
            "description",
            "dataset",
            "definition",
            "created_by",
            "created_by_email",
            "is_system",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_by", "created_by_email", "is_system", "created_at", "updated_at"]

    def validate_definition(self, value):
        if value is None:
            return {}
        if not isinstance(value, dict):
            raise serializers.ValidationError("definition must be an object")

        # Basic shape checks to fail fast
        for k in ("fields", "filters", "order_by", "group_by", "aggregations"):
            if k in value and value[k] is not None and not isinstance(value[k], list):
                raise serializers.ValidationError(f"{k} must be a list")
        if "limit" in value and value["limit"] is not None:
            try:
                lim = int(value["limit"])
                if lim <= 0:
                    raise ValueError
            except Exception:
                raise serializers.ValidationError("limit must be a positive integer")
        return value

    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user and request.user.is_authenticated:
            validated_data["created_by"] = request.user
        return super().create(validated_data)
