from rest_framework import viewsets, permissions, decorators, status
from rest_framework.response import Response

from accounts.permissions import RolePermission
from accounts.models import User
from audit.mixins import AuditMixin
from .models import AppraisalTemplate, Appraisal, Goal
from .serializers import AppraisalTemplateSerializer, AppraisalSerializer, GoalSerializer

class AppraisalTemplateViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = AppraisalTemplate.objects.all()
    serializer_class = AppraisalTemplateSerializer
    allowed_roles = [User.Role.SYSTEM_ADMIN, User.Role.HR_MANAGER, User.Role.HR_OFFICER]
    permission_classes = [permissions.IsAuthenticated, RolePermission]

class AppraisalViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = Appraisal.objects.select_related("employee", "employee__user", "template").all()
    serializer_class = AppraisalSerializer
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

    @decorators.action(detail=True, methods=["post"])
    def submit(self, request, *args, **kwargs):
        appraisal = self.get_object()
        appraisal.status = Appraisal.Status.SUBMITTED
        appraisal.save(update_fields=["status"])
        self.audit_log("UPDATE", appraisal, {"field": "status", "to": "SUBMITTED"})
        return Response({"detail": "Submitted."})

    @decorators.action(detail=True, methods=["post"])
    def supervisor_review(self, request, *args, **kwargs):
        appraisal = self.get_object()
        if request.user.role not in [User.Role.LINE_MANAGER, User.Role.SYSTEM_ADMIN]:
            return Response({"detail": "Not allowed."}, status=status.HTTP_403_FORBIDDEN)
        appraisal.status = Appraisal.Status.SUPERVISOR_REVIEW
        appraisal.supervisor_feedback = request.data.get("supervisor_feedback", appraisal.supervisor_feedback)
        appraisal.save(update_fields=["status", "supervisor_feedback"])
        self.audit_log("UPDATE", appraisal, {"field": "status", "to": "SUPERVISOR_REVIEW", "info": "Supervisor review saved"})
        return Response({"detail": "Supervisor review saved."})

    @decorators.action(detail=True, methods=["post"])
    def hr_review(self, request, *args, **kwargs):
        appraisal = self.get_object()
        if request.user.role not in [User.Role.HR_MANAGER, User.Role.HR_OFFICER, User.Role.SYSTEM_ADMIN]:
            return Response({"detail": "Not allowed."}, status=status.HTTP_403_FORBIDDEN)
        appraisal.status = Appraisal.Status.HR_REVIEW
        appraisal.hr_notes = request.data.get("hr_notes", appraisal.hr_notes)
        appraisal.save(update_fields=["status", "hr_notes"])
        self.audit_log("UPDATE", appraisal, {"field": "status", "to": "HR_REVIEW", "info": "HR review saved"})
        return Response({"detail": "HR review saved."})

    @decorators.action(detail=True, methods=["post"])
    def finalize(self, request, *args, **kwargs):
        appraisal = self.get_object()
        if request.user.role not in [User.Role.HR_MANAGER, User.Role.SYSTEM_ADMIN]:
            return Response({"detail": "Not allowed."}, status=status.HTTP_403_FORBIDDEN)
        appraisal.status = Appraisal.Status.FINALIZED
        appraisal.save(update_fields=["status"])
        self.audit_log("UPDATE", appraisal, {"field": "status", "to": "FINALIZED"})
        return Response({"detail": "Finalized."})

class GoalViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = Goal.objects.select_related("appraisal").all()
    serializer_class = GoalSerializer
    permission_classes = [permissions.IsAuthenticated]
