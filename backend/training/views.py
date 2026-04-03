from rest_framework import viewsets, permissions

from accounts.permissions import RolePermission
from accounts.models import User
from audit.mixins import AuditMixin

from .models import Competency, EmployeeCompetency, TrainingProgram, TrainingNeed, EmployeeTraining
from .serializers import (
    CompetencySerializer,
    EmployeeCompetencySerializer,
    TrainingProgramSerializer,
    TrainingNeedSerializer,
    EmployeeTrainingSerializer,
)


class CompetencyViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = Competency.objects.all()
    serializer_class = CompetencySerializer
    allowed_roles = [User.Role.SYSTEM_ADMIN, User.Role.HR_MANAGER, User.Role.HR_OFFICER]
    permission_classes = [permissions.IsAuthenticated, RolePermission]


class EmployeeCompetencyViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = EmployeeCompetency.objects.select_related("employee", "employee__user", "competency").all()
    serializer_class = EmployeeCompetencySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        if user.role == User.Role.EMPLOYEE:
            emp = getattr(user, "employee_profile", None)
            return qs.filter(employee=emp) if emp else qs.none()
        if user.role == User.Role.LINE_MANAGER:
            dept = getattr(getattr(user, "employee_profile", None), "department", None)
            return qs.filter(employee__department=dept) if dept else qs.none()
        return qs

    def get_permissions(self):
        if self.request.method in ("POST", "PUT", "PATCH", "DELETE"):
            self.allowed_roles = [User.Role.SYSTEM_ADMIN, User.Role.HR_MANAGER, User.Role.HR_OFFICER]
            return [permissions.IsAuthenticated(), RolePermission()]
        return [permissions.IsAuthenticated()]


class TrainingProgramViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = TrainingProgram.objects.all()
    serializer_class = TrainingProgramSerializer
    allowed_roles = [User.Role.SYSTEM_ADMIN, User.Role.HR_MANAGER, User.Role.HR_OFFICER]
    permission_classes = [permissions.IsAuthenticated, RolePermission]


class TrainingNeedViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = TrainingNeed.objects.select_related("employee", "employee__user", "department", "competency", "identified_by").all()
    serializer_class = TrainingNeedSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        if user.role == User.Role.EMPLOYEE:
            emp = getattr(user, "employee_profile", None)
            return qs.filter(employee=emp) if emp else qs.none()
        if user.role == User.Role.LINE_MANAGER:
            dept = getattr(getattr(user, "employee_profile", None), "department", None)
            return qs.filter(department=dept) if dept else qs.none()
        return qs

    def get_permissions(self):
        if self.request.method in ("POST", "PUT", "PATCH", "DELETE"):
            self.allowed_roles = [User.Role.SYSTEM_ADMIN, User.Role.HR_MANAGER, User.Role.HR_OFFICER, User.Role.LINE_MANAGER]
            return [permissions.IsAuthenticated(), RolePermission()]
        return [permissions.IsAuthenticated()]


class EmployeeTrainingViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = EmployeeTraining.objects.select_related("employee", "employee__user", "program", "recorded_by").all()
    serializer_class = EmployeeTrainingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        if user.role == User.Role.EMPLOYEE:
            emp = getattr(user, "employee_profile", None)
            return qs.filter(employee=emp) if emp else qs.none()
        if user.role == User.Role.LINE_MANAGER:
            dept = getattr(getattr(user, "employee_profile", None), "department", None)
            return qs.filter(employee__department=dept) if dept else qs.none()
        return qs

    def get_permissions(self):
        if self.request.method in ("POST", "PUT", "PATCH", "DELETE"):
            self.allowed_roles = [User.Role.SYSTEM_ADMIN, User.Role.HR_MANAGER, User.Role.HR_OFFICER]
            return [permissions.IsAuthenticated(), RolePermission()]
        return [permissions.IsAuthenticated()]
