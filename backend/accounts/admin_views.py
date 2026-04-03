from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from rest_framework import viewsets, permissions, decorators, status
from rest_framework.response import Response

from audit.mixins import AuditMixin
from accounts.permissions import RolePermission
from accounts.models import User

from .admin_serializers import AdminUserSerializer, GroupSerializer, PermissionSerializer


UserModel = get_user_model()


class UserViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = UserModel.objects.all().order_by("email")
    serializer_class = AdminUserSerializer
    allowed_roles = [User.Role.SYSTEM_ADMIN, User.Role.HR_MANAGER]
    permission_classes = [permissions.IsAuthenticated, RolePermission]
    audit_model_name = "User"
    audit_fields = ["email", "first_name", "last_name", "role", "is_active", "is_staff", "is_superuser"]

    @decorators.action(detail=True, methods=["post"], url_path="set_password")
    def set_password(self, request, *args, **kwargs):
        user = self.get_object()
        password = request.data.get("password", "")
        if not password or len(password) < 8:
            return Response({"detail": "Password must be at least 8 characters."}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(password)
        user.save(update_fields=["password"])
        self.audit_log("UPDATE", user, {"field": "password", "info": "Password changed by admin"})
        return Response({"detail": "Password updated."})


class GroupViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = Group.objects.prefetch_related("permissions").all().order_by("name")
    serializer_class = GroupSerializer
    allowed_roles = [User.Role.SYSTEM_ADMIN]
    permission_classes = [permissions.IsAuthenticated, RolePermission]
    audit_model_name = "Group"
    audit_fields = ["name"]


class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Permission.objects.select_related("content_type").all().order_by("content_type__app_label", "codename")
    serializer_class = PermissionSerializer
    allowed_roles = [User.Role.SYSTEM_ADMIN]
    permission_classes = [permissions.IsAuthenticated, RolePermission]
