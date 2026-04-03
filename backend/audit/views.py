from rest_framework import viewsets, permissions

from accounts.models import User
from accounts.permissions import RolePermission

from .models import AuditLog
from .serializers import AuditLogSerializer


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only access to audit logs for privileged roles."""

    queryset = AuditLog.objects.select_related("actor").all()
    serializer_class = AuditLogSerializer
    allowed_roles = [User.Role.SYSTEM_ADMIN, User.Role.HR_MANAGER]
    permission_classes = [permissions.IsAuthenticated, RolePermission]
