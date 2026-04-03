from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import UserInvite


User = get_user_model()


class InviteCreateSerializer(serializers.Serializer):
    email = serializers.EmailField()
    first_name = serializers.CharField(required=False, allow_blank=True, max_length=80)
    last_name = serializers.CharField(required=False, allow_blank=True, max_length=80)
    role = serializers.ChoiceField(choices=User.Role.choices, default=User.Role.EMPLOYEE)
    auto_activate = serializers.BooleanField(default=False)
    expires_in_days = serializers.IntegerField(required=False, min_value=1, max_value=90)


class InviteSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    created_by_email = serializers.CharField(source="created_by.email", read_only=True)

    class Meta:
        model = UserInvite
        fields = [
            "id",
            "email",
            "role",
            "auto_activate",
            "created_at",
            "expires_at",
            "used_at",
            "status",
            "created_by",
            "created_by_email",
            "user",
        ]
        read_only_fields = fields

    def get_status(self, obj):
        return obj.status


class InviteValidateResponseSerializer(serializers.Serializer):
    email = serializers.EmailField()
    full_name = serializers.CharField()
    role = serializers.CharField()
    expires_at = serializers.DateTimeField()
    auto_activate = serializers.BooleanField()


class InviteAcceptSerializer(serializers.Serializer):
    token = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, min_length=8)
