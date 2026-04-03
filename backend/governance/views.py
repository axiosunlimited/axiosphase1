from rest_framework import viewsets, permissions

from accounts.permissions import RolePermission
from accounts.models import User
from audit.mixins import AuditMixin

from .models import (
    ApprovalProcessConfig,
    Policy,
    PolicyAcknowledgement,
    DisciplinaryCase,
    Grievance,
    ComplianceItem,
)
from .serializers import (
    ApprovalProcessConfigSerializer,
    PolicySerializer,
    PolicyAcknowledgementSerializer,
    DisciplinaryCaseSerializer,
    GrievanceSerializer,
    ComplianceItemSerializer,
)


class ApprovalProcessConfigViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = ApprovalProcessConfig.objects.all().order_by("process_code")
    serializer_class = ApprovalProcessConfigSerializer
    allowed_roles = [User.Role.SYSTEM_ADMIN, User.Role.HR_MANAGER]
    permission_classes = [permissions.IsAuthenticated, RolePermission]


class PolicyViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = Policy.objects.all()
    serializer_class = PolicySerializer
    allowed_roles = [User.Role.SYSTEM_ADMIN, User.Role.HR_MANAGER, User.Role.HR_OFFICER]
    permission_classes = [permissions.IsAuthenticated, RolePermission]


class PolicyAcknowledgementViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = PolicyAcknowledgement.objects.select_related("policy", "employee").all()
    serializer_class = PolicyAcknowledgementSerializer
    allowed_roles = [User.Role.SYSTEM_ADMIN, User.Role.HR_MANAGER, User.Role.HR_OFFICER]
    permission_classes = [permissions.IsAuthenticated, RolePermission]


class DisciplinaryCaseViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = DisciplinaryCase.objects.select_related("employee", "created_by").all()
    serializer_class = DisciplinaryCaseSerializer
    allowed_roles = [User.Role.SYSTEM_ADMIN, User.Role.HR_MANAGER, User.Role.HR_OFFICER]
    permission_classes = [permissions.IsAuthenticated, RolePermission]


class GrievanceViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = Grievance.objects.select_related("employee").all()
    serializer_class = GrievanceSerializer
    allowed_roles = [User.Role.SYSTEM_ADMIN, User.Role.HR_MANAGER, User.Role.HR_OFFICER]
    permission_classes = [permissions.IsAuthenticated, RolePermission]


class ComplianceItemViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = ComplianceItem.objects.all()
    serializer_class = ComplianceItemSerializer
    allowed_roles = [User.Role.SYSTEM_ADMIN, User.Role.HR_MANAGER, User.Role.HR_OFFICER]
    permission_classes = [permissions.IsAuthenticated, RolePermission]
