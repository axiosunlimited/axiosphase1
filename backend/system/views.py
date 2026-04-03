from __future__ import annotations

from rest_framework import viewsets, permissions, decorators, status
from rest_framework.response import Response
from django.http import FileResponse

from accounts.models import User
from accounts.permissions import RolePermission
from audit.mixins import AuditMixin

from .models import SystemSetting, BackupArtifact
from .serializers import SystemSettingSerializer, BackupArtifactSerializer
from .utils import create_backup


class SystemSettingViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = SystemSetting.objects.all()
    serializer_class = SystemSettingSerializer
    allowed_roles = [User.Role.SYSTEM_ADMIN]
    permission_classes = [permissions.IsAuthenticated, RolePermission]


class BackupArtifactViewSet(AuditMixin, viewsets.ReadOnlyModelViewSet):
    queryset = BackupArtifact.objects.select_related("created_by").all()
    serializer_class = BackupArtifactSerializer
    allowed_roles = [User.Role.SYSTEM_ADMIN, User.Role.HR_MANAGER, User.Role.HR_OFFICER]
    permission_classes = [permissions.IsAuthenticated, RolePermission]

    @decorators.action(detail=False, methods=["post"])
    def run_backup(self, request, *args, **kwargs):
        # Manual backup trigger
        obj = create_backup(created_by=request.user)
        self.audit_log("CREATE", obj, {"info": "Manual backup created"})
        return Response(BackupArtifactSerializer(obj).data, status=status.HTTP_201_CREATED)

    @decorators.action(detail=True, methods=["get"])
    def download(self, request, pk=None, *args, **kwargs):
        obj = self.get_object()
        self.audit_log("READ", obj, {"info": "Backup downloaded"})
        return FileResponse(obj.file.open("rb"), as_attachment=True, filename=obj.file.name.split("/")[-1])
