from rest_framework import serializers

from .models import Notification, Feedback, NotificationSetting, EmailTemplate, SystemAlert


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["id", "user", "title", "message", "is_read", "created_at"]
        read_only_fields = ["created_at"]


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ["id", "user", "category", "message", "page", "created_at"]
        read_only_fields = ["created_at", "user"]


class NotificationSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationSetting
        fields = ["id", "key", "enabled", "config", "updated_at"]
        read_only_fields = ["updated_at"]


class EmailTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailTemplate
        fields = ["id", "key", "enabled", "subject_template", "body_template", "updated_at"]
        read_only_fields = ["updated_at"]


class SystemAlertSerializer(serializers.ModelSerializer):
    employee_number = serializers.CharField(source="employee.employee_number", read_only=True, default=None)
    employee_name = serializers.CharField(source="employee.user.full_name", read_only=True, default=None)

    class Meta:
        model = SystemAlert
        fields = [
            "id", "alert_type", "title", "message",
            "employee", "employee_number", "employee_name",
            "target_user", "status", "metadata",
            "resolved_by", "resolved_at",
            "created_at", "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]
