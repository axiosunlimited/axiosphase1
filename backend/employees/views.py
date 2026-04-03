from rest_framework import viewsets, permissions, decorators, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from accounts.permissions import RolePermission
from audit.mixins import AuditMixin
from accounts.models import User

from .models import Department, Position, Employee, EmployeeDocument, Qualification, EmploymentHistory
from .serializers import (
    DepartmentSerializer,
    PositionSerializer,
    EmployeeSerializer,
    EmployeeDocumentSerializer,
    QualificationCRUDSerializer,
    EmploymentHistorySerializer,
)


class DepartmentViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    allowed_roles = [User.Role.SYSTEM_ADMIN, User.Role.HR_MANAGER, User.Role.HR_OFFICER]
    permission_classes = [permissions.IsAuthenticated, RolePermission]


class PositionViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = Position.objects.select_related("department").all()
    serializer_class = PositionSerializer
    allowed_roles = [User.Role.SYSTEM_ADMIN, User.Role.HR_MANAGER, User.Role.HR_OFFICER]
    permission_classes = [permissions.IsAuthenticated, RolePermission]


class EmployeeViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = Employee.objects.select_related("user", "department", "position").all()
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        if user.role == User.Role.EMPLOYEE:
            return qs.filter(user=user)
        if user.role == User.Role.LINE_MANAGER:
            return qs.filter(line_manager=user)
        return qs

    def get_permissions(self):
        # HR and admins can modify, employees can view/update own profile only
        if self.request.method in ("POST", "DELETE"):
            self.allowed_roles = [User.Role.SYSTEM_ADMIN, User.Role.HR_MANAGER, User.Role.HR_OFFICER]
            return [permissions.IsAuthenticated(), RolePermission()]
        if self.request.method in ("PUT", "PATCH"):
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]

    def perform_update(self, serializer):
        user = self.request.user
        if user.role == User.Role.EMPLOYEE:
            # Self-service: only allow updating contact and personal fields
            allowed = {"phone", "address", "date_of_birth"}
            inst = serializer.instance
            before = {k: getattr(inst, k, None) for k in allowed}
            data = {k: v for k, v in serializer.validated_data.items() if k in allowed}
            obj = serializer.save(**data)
            after = {k: getattr(obj, k, None) for k in allowed}
            changes = {k: {"from": before.get(k), "to": after.get(k)} for k in allowed if before.get(k) != after.get(k)}
            self.audit_log("UPDATE", obj, changes or {"info": "Employee self-service update"})
            return

        obj = serializer.save()
        # AuditMixin normally handles this, but we override perform_update.
        self.audit_log("UPDATE", obj, {"info": "Employee updated"})


class EmployeeDocumentViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = EmployeeDocument.objects.select_related("employee", "employee__user").all()
    serializer_class = EmployeeDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        if user.role == User.Role.EMPLOYEE:
            emp = getattr(user, "employee_profile", None)
            return qs.filter(employee=emp) if emp else qs.none()
        # Access to documents is restricted to HR/Admin (employees can see metadata for their own uploads).
        if user.role == User.Role.LINE_MANAGER:
            return qs.none()
        return qs

    def get_permissions(self):
        if self.request.method in ("POST", "PUT", "PATCH", "DELETE"):
            # Employees can upload their own documents; HR/Admin can manage any
            self.allowed_roles = [User.Role.SYSTEM_ADMIN, User.Role.HR_MANAGER, User.Role.HR_OFFICER, User.Role.EMPLOYEE]
            return [permissions.IsAuthenticated(), RolePermission()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        user = self.request.user
        if user.role == User.Role.EMPLOYEE:
            emp = getattr(user, "employee_profile", None)
            if not emp:
                raise ValidationError({"detail": "Employee profile missing"})
            obj = serializer.save(employee=emp)
        else:
            obj = serializer.save()

        # AuditMixin normally handles this, but we override perform_create.
        self.audit_log(
            "CREATE",
            obj,
            {
                "category": getattr(obj, "category", None),
                "employee_id": getattr(obj.employee, "id", None) if getattr(obj, "employee", None) else None,
                "original_name": getattr(obj, "original_name", None),
                "version": getattr(obj, "version", None),
            },
        )

    @decorators.action(detail=True, methods=["get"])
    def download(self, request, pk=None, *args, **kwargs):
        from django.http import HttpResponse
        from config.crypto import decrypt_bytes

        doc = self.get_object()
        if request.user.role == User.Role.EMPLOYEE:
            emp = getattr(request.user, "employee_profile", None)
            if not emp or doc.employee_id != emp.id:
                return Response({"detail": "Not allowed."}, status=status.HTTP_403_FORBIDDEN)
        elif request.user.role not in [User.Role.SYSTEM_ADMIN, User.Role.HR_MANAGER, User.Role.HR_OFFICER]:
            return Response({"detail": "Not allowed."}, status=status.HTTP_403_FORBIDDEN)

        raw = doc.encrypted_file.open("rb").read()
        data = decrypt_bytes(raw)
        self.audit_log("READ", doc, {"info": "Employee document downloaded"})
        resp = HttpResponse(data, content_type=doc.content_type or "application/octet-stream")
        resp["Content-Disposition"] = f'attachment; filename="{doc.original_name}"'
        return resp


class QualificationViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = Qualification.objects.select_related("employee", "employee__user").all()
    serializer_class = QualificationCRUDSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        if user.role == User.Role.EMPLOYEE:
            emp = getattr(user, "employee_profile", None)
            return qs.filter(employee=emp) if emp else qs.none()
        if user.role == User.Role.LINE_MANAGER:
            return qs.filter(employee__line_manager=user)
        return qs

    def get_permissions(self):
        if self.request.method in ("POST", "PUT", "PATCH", "DELETE"):
            self.allowed_roles = [User.Role.SYSTEM_ADMIN, User.Role.HR_MANAGER, User.Role.HR_OFFICER]
            return [permissions.IsAuthenticated(), RolePermission()]
        return [permissions.IsAuthenticated()]


class EmploymentHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EmploymentHistory.objects.select_related("employee", "employee__user", "department", "position").all()
    serializer_class = EmploymentHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        employee_id = self.request.query_params.get("employee_id")
        if employee_id:
            try:
                employee_id = int(employee_id)
                qs = qs.filter(employee_id=employee_id)
            except Exception:
                pass

        if user.role == User.Role.EMPLOYEE:
            emp = getattr(user, "employee_profile", None)
            return qs.filter(employee=emp) if emp else qs.none()
        if user.role == User.Role.LINE_MANAGER:
            return qs.filter(employee__line_manager=user)
        return qs
