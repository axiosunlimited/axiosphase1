from rest_framework import viewsets, permissions

from accounts.permissions import RolePermission
from accounts.models import User
from audit.mixins import AuditMixin

from .models import EstablishmentItem, Separation
from .serializers import EstablishmentItemSerializer, SeparationSerializer


class EstablishmentItemViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = EstablishmentItem.objects.select_related("department", "position").all()
    serializer_class = EstablishmentItemSerializer
    allowed_roles = [User.Role.SYSTEM_ADMIN, User.Role.HR_MANAGER, User.Role.HR_OFFICER]
    permission_classes = [permissions.IsAuthenticated, RolePermission]


class SeparationViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = Separation.objects.select_related("employee", "employee__user").all()
    serializer_class = SeparationSerializer
    allowed_roles = [User.Role.SYSTEM_ADMIN, User.Role.HR_MANAGER, User.Role.HR_OFFICER]
    permission_classes = [permissions.IsAuthenticated, RolePermission]
