from rest_framework import viewsets, permissions, decorators
from rest_framework.response import Response

from audit.mixins import AuditMixin
from accounts.models import User
from accounts.permissions import RolePermission

from django.utils import timezone

from .models import Notification, Feedback, NotificationSetting, EmailTemplate, SystemAlert
from .serializers import (
    NotificationSerializer,
    FeedbackSerializer,
    NotificationSettingSerializer,
    EmailTemplateSerializer,
    SystemAlertSerializer,
)


class NotificationViewSet(AuditMixin, viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role in [User.Role.SYSTEM_ADMIN, User.Role.HR_MANAGER, User.Role.HR_OFFICER]:
            return Notification.objects.select_related("user").all()
        return Notification.objects.filter(user=user)

    def perform_create(self, serializer):
        # allow admins to send notifications to any user
        if self.request.user.role in [User.Role.SYSTEM_ADMIN, User.Role.HR_MANAGER, User.Role.HR_OFFICER]:
            if "user" in serializer.validated_data:
                obj = serializer.save()
            else:
                obj = serializer.save(user=self.request.user)
        else:
            obj = serializer.save(user=self.request.user)

        # AuditMixin normally handles this, but we override perform_create.
        self.audit_log(
            "CREATE",
            obj,
            {
                "user_id": getattr(obj.user, "id", None) if getattr(obj, "user", None) else None,
                "title": getattr(obj, "title", None),
            },
        )

    @decorators.action(detail=True, methods=["post"])
    def mark_read(self, request, *args, **kwargs):
        notif = self.get_object()
        notif.is_read = True
        notif.save(update_fields=["is_read"])
        self.audit_log("UPDATE", notif, {"field": "is_read", "to": True})
        return Response({"detail": "Marked as read."})


class FeedbackViewSet(AuditMixin, viewsets.ModelViewSet):
    serializer_class = FeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role in [User.Role.SYSTEM_ADMIN, User.Role.HR_MANAGER]:
            return Feedback.objects.select_related("user").all()
        return Feedback.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        obj = serializer.save(user=self.request.user)
        self.audit_log(
            "CREATE",
            obj,
            {"category": getattr(obj, "category", None), "page": getattr(obj, "page", None)},
        )


class NotificationSettingViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = NotificationSetting.objects.all()
    serializer_class = NotificationSettingSerializer
    allowed_roles = [User.Role.SYSTEM_ADMIN]
    permission_classes = [permissions.IsAuthenticated, RolePermission]


class EmailTemplateViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = EmailTemplate.objects.all()
    serializer_class = EmailTemplateSerializer
    allowed_roles = [User.Role.SYSTEM_ADMIN]
    permission_classes = [permissions.IsAuthenticated, RolePermission]


class SystemAlertViewSet(AuditMixin, viewsets.ModelViewSet):
    serializer_class = SystemAlertSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = SystemAlert.objects.select_related("employee", "employee__user", "target_user", "resolved_by").all()

        # Filter by status query param
        status_filter = self.request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter)

        # Filter by alert_type query param
        alert_type = self.request.query_params.get("alert_type")
        if alert_type:
            qs = qs.filter(alert_type=alert_type)

        # HR/Admin see all; others see only their own
        if user.role in [User.Role.SYSTEM_ADMIN, User.Role.HR_MANAGER, User.Role.HR_OFFICER]:
            return qs
        return qs.filter(target_user=user)

    def get_permissions(self):
        if self.request.method in ("POST", "DELETE"):
            self.allowed_roles = [User.Role.SYSTEM_ADMIN, User.Role.HR_MANAGER, User.Role.HR_OFFICER]
            return [permissions.IsAuthenticated(), RolePermission()]
        return [permissions.IsAuthenticated()]

    @decorators.action(detail=True, methods=["post"])
    def resolve(self, request, *args, **kwargs):
        alert = self.get_object()
        alert.status = SystemAlert.Status.RESOLVED
        alert.resolved_by = request.user
        alert.resolved_at = timezone.now()
        alert.save(update_fields=["status", "resolved_by", "resolved_at", "updated_at"])
        self.audit_log("UPDATE", alert, {"status": "RESOLVED"})
        return Response(SystemAlertSerializer(alert).data)

    @decorators.action(detail=True, methods=["post"])
    def dismiss(self, request, *args, **kwargs):
        alert = self.get_object()
        alert.status = SystemAlert.Status.DISMISSED
        alert.resolved_by = request.user
        alert.resolved_at = timezone.now()
        alert.save(update_fields=["status", "resolved_by", "resolved_at", "updated_at"])
        self.audit_log("UPDATE", alert, {"status": "DISMISSED"})
        return Response(SystemAlertSerializer(alert).data)

    @decorators.action(detail=True, methods=["post"])
    def acknowledge(self, request, *args, **kwargs):
        alert = self.get_object()
        alert.status = SystemAlert.Status.ACKNOWLEDGED
        alert.save(update_fields=["status", "updated_at"])
        self.audit_log("UPDATE", alert, {"status": "ACKNOWLEDGED"})
        return Response(SystemAlertSerializer(alert).data)
