from rest_framework import viewsets, permissions, decorators, status
from rest_framework.response import Response
from django.http import FileResponse
from io import BytesIO
from reportlab.pdfgen import canvas

from accounts.permissions import RolePermission
from accounts.models import User
from audit.mixins import AuditMixin
from governance.utils import allowed_roles_for
from governance.models import ApprovalProcessConfig

from .models import Vacancy, Applicant, Interview, Appointment
from .serializers import VacancySerializer, ApplicantSerializer, InterviewSerializer, AppointmentSerializer
from notifications.utils import notify_user


class VacancyViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = Vacancy.objects.select_related("department", "position").all()
    serializer_class = VacancySerializer
    allowed_roles = [User.Role.SYSTEM_ADMIN, User.Role.HR_MANAGER, User.Role.HR_OFFICER]
    permission_classes = [permissions.IsAuthenticated, RolePermission]

    @decorators.action(detail=True, methods=["post"])
    def submit(self, request, *args, **kwargs):
        vacancy = self.get_object()
        vacancy.status = Vacancy.Status.SUBMITTED
        vacancy.save(update_fields=["status"])
        self.audit_log("UPDATE", vacancy, {"field": "status", "to": "SUBMITTED"})
        return Response({"detail": "Submitted for approval."})

    @decorators.action(detail=True, methods=["post"])
    def approve(self, request, *args, **kwargs):
        vacancy = self.get_object()
        allowed = allowed_roles_for(
            ApprovalProcessConfig.Process.VACANCY_APPROVAL,
            default_roles=[User.Role.HR_MANAGER, User.Role.SYSTEM_ADMIN],
        )
        if request.user.role not in allowed:
            return Response({"detail": "Not allowed."}, status=status.HTTP_403_FORBIDDEN)

        vacancy.status = Vacancy.Status.APPROVED
        vacancy.save(update_fields=["status"])
        self.audit_log("UPDATE", vacancy, {"field": "status", "to": "APPROVED"})
        return Response({"detail": "Approved."})

    @decorators.action(detail=True, methods=["post"])
    def publish(self, request, *args, **kwargs):
        vacancy = self.get_object()
        allowed = allowed_roles_for(
            ApprovalProcessConfig.Process.VACANCY_PUBLISH,
            default_roles=[User.Role.HR_MANAGER, User.Role.HR_OFFICER, User.Role.SYSTEM_ADMIN],
        )
        if request.user.role not in allowed:
            return Response({"detail": "Not allowed."}, status=status.HTTP_403_FORBIDDEN)

        vacancy.status = Vacancy.Status.PUBLISHED
        vacancy.save(update_fields=["status"])
        self.audit_log("UPDATE", vacancy, {"field": "status", "to": "PUBLISHED"})

        # Vacancy announcement to staff (configurable notifications)
        try:
            msg = f"New vacancy published: {vacancy.title} (Closing: {vacancy.closing_date.isoformat() if vacancy.closing_date else 'TBA'})"
            for u in User.objects.filter(is_active=True):
                notify_user(u, key="vacancy_published", context={"message": msg, "vacancy_id": vacancy.id}, title="Vacancy Published")
        except Exception:
            pass
        return Response({"detail": "Published."})


class ApplicantViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = Applicant.objects.select_related("vacancy", "vacancy__department", "vacancy__position").all()
    serializer_class = ApplicantSerializer

    def get_queryset(self):
        # Public can only create. All other actions require HR access.
        return super().get_queryset()

    def get_permissions(self):
        if self.action in ("create",):
            # allow public applications
            return [permissions.AllowAny()]
        self.allowed_roles = [User.Role.SYSTEM_ADMIN, User.Role.HR_MANAGER, User.Role.HR_OFFICER]
        return [permissions.IsAuthenticated(), RolePermission()]


class InterviewViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = Interview.objects.select_related("applicant", "applicant__vacancy").all()
    serializer_class = InterviewSerializer
    allowed_roles = [User.Role.SYSTEM_ADMIN, User.Role.HR_MANAGER, User.Role.HR_OFFICER, User.Role.LINE_MANAGER]
    permission_classes = [permissions.IsAuthenticated, RolePermission]


class AppointmentViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = Appointment.objects.select_related("applicant", "applicant__vacancy", "applicant__vacancy__department").all()
    serializer_class = AppointmentSerializer
    allowed_roles = [User.Role.SYSTEM_ADMIN, User.Role.HR_MANAGER, User.Role.HR_OFFICER]
    permission_classes = [permissions.IsAuthenticated, RolePermission]

    @decorators.action(detail=True, methods=["get"])
    def letter(self, request, *args, **kwargs):
        appointment = self.get_object()
        applicant = appointment.applicant
        vacancy = applicant.vacancy

        buffer = BytesIO()
        c = canvas.Canvas(buffer)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(72, 780, "Appointment Letter")
        c.setFont("Helvetica", 11)
        y = 740
        lines = [
            f"To: {applicant.first_name} {applicant.last_name}",
            f"Email: {applicant.email}",
            "",
            f"Re: Appointment - {vacancy.title}",
            "",
            f"We are pleased to offer you an appointment for the position of {vacancy.position.title}",
            f"in the {vacancy.department.name} department.",
            f"Start Date: {appointment.start_date.isoformat()}",
        ]
        for line in lines:
            c.drawString(72, y, line)
            y -= 18
        c.showPage()
        c.save()
        buffer.seek(0)
        filename = f"appointment_letter_{appointment.id}.pdf"
        self.audit_log("READ", appointment, {"info": "Appointment letter generated/downloaded"})
        return FileResponse(buffer, as_attachment=True, filename=filename)
