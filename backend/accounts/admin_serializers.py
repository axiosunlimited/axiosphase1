from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from rest_framework import serializers

User = get_user_model()


class PermissionSerializer(serializers.ModelSerializer):
    content_type = serializers.SerializerMethodField()

    def get_content_type(self, obj):
        ct = obj.content_type
        return {"id": ct.id, "app_label": ct.app_label, "model": ct.model}

    class Meta:
        model = Permission
        fields = ["id", "name", "codename", "content_type"]


class GroupSerializer(serializers.ModelSerializer):
    permissions = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Permission.objects.all(), required=False
    )

    class Meta:
        model = Group
        fields = ["id", "name", "permissions"]


class AdminUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=True, min_length=8)
    groups = serializers.PrimaryKeyRelatedField(many=True, queryset=Group.objects.all(), required=False)
    user_permissions = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Permission.objects.all(), required=False
    )

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "role",
            "is_active",
            "is_staff",
            "is_superuser",
            "twofa_enabled",
            "failed_login_attempts",
            "locked_until",
            "date_joined",
            "groups",
            "user_permissions",
            "password",
        ]
        read_only_fields = ["failed_login_attempts", "locked_until", "date_joined", "twofa_enabled"]

    def create(self, validated_data):
        password = validated_data.pop("password", "")
        groups = validated_data.pop("groups", [])
        perms = validated_data.pop("user_permissions", [])
        user = User.objects.create_user(password=password or None, **validated_data)
        if groups:
            user.groups.set(groups)
        if perms:
            user.user_permissions.set(perms)
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", "")
        groups = validated_data.pop("groups", None)
        perms = validated_data.pop("user_permissions", None)
        for k, v in validated_data.items():
            setattr(instance, k, v)
        if password:
            instance.set_password(password)
        instance.save()
        if groups is not None:
            instance.groups.set(groups)
        if perms is not None:
            instance.user_permissions.set(perms)
        return instance
