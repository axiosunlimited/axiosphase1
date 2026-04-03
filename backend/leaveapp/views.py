from rest_framework import viewsets, permissions, decorators, status
from rest_framework.response import Response
from django.utils import timezone

from accounts.permissions import RolePermission
from accounts.models import User
from audit.mixins import AuditMixin
from governance.utils import allowed_roles_for
from governance.models import ApprovalProcessConfig

from .models import LeaveType, LeaveBalance, LeaveRequest, PublicHoliday
from .serializers import LeaveTypeSerializer, LeaveBalanceSerializer, LeaveRequestSerializer, PublicHolidaySerializer
from notifications.utils import notify_user, send_email_message
from django.conf import settings


class LeaveTypeViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = LeaveType.objects.all()
    serializer_class = LeaveTypeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.request.method not in ("GET", "HEAD", "OPTIONS"):
            self.allowed_roles = [User.Role.SYSTEM_ADMIN, User.Role.HR_MANAGER, User.Role.HR_OFFICER]
            return [permissions.IsAuthenticated(), RolePermission()]
        return [permissions.IsAuthenticated()]


class LeaveBalanceViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = LeaveBalance.objects.select_related("employee", "leave_type", "employee__user").all()
    serializer_class = LeaveBalanceSerializer
    allowed_roles = [User.Role.SYSTEM_ADMIN, User.Role.HR_MANAGER, User.Role.HR_OFFICER, User.Role.EMPLOYEE, User.Role.LINE_MANAGER]
    permission_classes = [permissions.IsAuthenticated, RolePermission]

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        if user.role == User.Role.EMPLOYEE:
            emp = getattr(user, "employee_profile", None)
            if emp:
                return qs.filter(employee=emp)
            return qs.none()
        if user.role == User.Role.LINE_MANAGER:
            return qs.filter(employee__line_manager=user)
        return qs


class LeaveRequestViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = LeaveRequest.objects.select_related("employee", "leave_type", "employee__user").all()
    serializer_class = LeaveRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        if user.role == User.Role.EMPLOYEE:
            emp = getattr(user, "employee_profile", None)
            if emp:
                return qs.filter(employee=emp)
            return qs.none()
        if user.role == User.Role.LINE_MANAGER:
            return qs.filter(employee__line_manager=user)
        if user.role == User.Role.PVC:
            return qs.filter(status=LeaveRequest.Status.PENDING_PVC)
        if user.role == User.Role.ADMIN_OFFICER:
            return qs.filter(status=LeaveRequest.Status.PENDING_ADMIN)
        if user.role == User.Role.FINANCE_OFFICER:
            return qs.filter(status=LeaveRequest.Status.PENDING_FINANCE)
        return qs

    def create(self, request, *args, **kwargs):
        # employees create for themselves
        if request.user.role == User.Role.EMPLOYEE:
            emp = getattr(request.user, "employee_profile", None)
            if not emp:
                return Response({"detail": "Employee profile missing."}, status=status.HTTP_400_BAD_REQUEST)
            if not emp.line_manager:
                return Response({"detail": "Line manager not assigned for this employee."}, status=status.HTTP_400_BAD_REQUEST)
            data = request.data.copy()
            data["employee_id"] = emp.id
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            obj = serializer.save(employee=emp, line_manager=emp.line_manager, status=LeaveRequest.Status.PENDING_LM)
            self.audit_log("CREATE", obj, {"info": "Leave request submitted"})
            notify_user(emp.line_manager, key="leave_submitted", context={"message": f"Leave request from {emp.user.full_name} ({emp.employee_number})", "leave_id": obj.id}, title="Leave Request")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return super().create(request, *args, **kwargs)

    @decorators.action(detail=True, methods=["post"])
    def approve_line_manager(self, request, *args, **kwargs):
        lr = self.get_object()
        allowed = allowed_roles_for(
            ApprovalProcessConfig.Process.LEAVE_LINE_MANAGER,
            default_roles=[User.Role.LINE_MANAGER, User.Role.SYSTEM_ADMIN],
        )
        if request.user.role not in allowed:
            return Response({"detail": "Not allowed."}, status=status.HTTP_403_FORBIDDEN)

        if lr.status in [LeaveRequest.Status.REJECTED, LeaveRequest.Status.CANCELLED, LeaveRequest.Status.APPROVED]:
            return Response({"detail": f"Cannot approve in status {lr.status}."}, status=status.HTTP_400_BAD_REQUEST)

        if lr.status != LeaveRequest.Status.PENDING_LM:
            return Response({"detail": f"Expected status PENDING_LM, got {lr.status}."}, status=status.HTTP_400_BAD_REQUEST)

        lr.status = LeaveRequest.Status.PENDING_HR
        lr.line_manager = request.user
        lr.save(update_fields=["status", "line_manager"])
        self.audit_log("UPDATE", lr, {"field": "status", "to": "PENDING_HR", "line_manager": request.user.email})
        notify_user(lr.employee.user, key="leave_lm_approved", context={"message": "Leave approved by line manager and sent to HR.", "leave_id": lr.id}, title="Leave Update")
        return Response({"detail": "Line manager approved."})

    @decorators.action(detail=True, methods=["post"])
    def approve_hr(self, request, *args, **kwargs):
        lr = self.get_object()
        allowed = allowed_roles_for(
            ApprovalProcessConfig.Process.LEAVE_HR,
            default_roles=[User.Role.HR_MANAGER, User.Role.HR_OFFICER, User.Role.SYSTEM_ADMIN],
        )
        if request.user.role not in allowed:
            return Response({"detail": "Not allowed."}, status=status.HTTP_403_FORBIDDEN)

        if lr.status in [LeaveRequest.Status.REJECTED, LeaveRequest.Status.CANCELLED, LeaveRequest.Status.APPROVED]:
            return Response({"detail": f"Cannot approve in status {lr.status}."}, status=status.HTTP_400_BAD_REQUEST)

        # Determine whether LM approval stage is required
        lm_cfg = ApprovalProcessConfig.objects.filter(process_code=ApprovalProcessConfig.Process.LEAVE_LINE_MANAGER, is_active=True).first()
        lm_stage_required = bool(lm_cfg and isinstance(lm_cfg.allowed_roles, list) and lm_cfg.allowed_roles)

        if lm_stage_required and lr.status != LeaveRequest.Status.PENDING_HR and request.user.role != User.Role.SYSTEM_ADMIN:
            return Response({"detail": "Must be line-manager approved first."}, status=status.HTTP_400_BAD_REQUEST)

        # Check leave balance but do NOT deduct until final approval
        year = lr.start_date.year
        balance, _ = LeaveBalance.objects.get_or_create(
            employee=lr.employee,
            leave_type=lr.leave_type,
            year=year,
            defaults={"days_entitled": lr.leave_type.default_days_per_year, "days_used": 0},
        )
        if balance.days_remaining < lr.days_requested:
            return Response(
                {"detail": "Insufficient leave balance.", "days_remaining": balance.days_remaining, "days_requested": lr.days_requested},
                status=status.HTTP_400_BAD_REQUEST,
            )

        lr.status = LeaveRequest.Status.PENDING_PVC
        lr.hr_officer = request.user
        lr.save(update_fields=["status", "hr_officer"])

        self.audit_log(
            "UPDATE",
            lr,
            {
                "field": "status",
                "to": "PENDING_PVC",
                "hr_officer": request.user.email,
                "balance_year": year,
                "days_checked": lr.days_requested,
            },
        )
        notify_user(lr.employee.user, key="leave_hr_confirmed", context={"message": "Leave confirmed by HR and sent for approvals.", "leave_id": lr.id}, title="Leave Update")
        return Response({"detail": "HR approved."})

    @decorators.action(detail=True, methods=["post"])
    def approve_pvc(self, request, *args, **kwargs):
        lr = self.get_object()
        allowed = allowed_roles_for(
            ApprovalProcessConfig.Process.LEAVE_PVC,
            default_roles=[User.Role.PVC, User.Role.SYSTEM_ADMIN],
        )
        if request.user.role not in allowed:
            return Response({"detail": "Not allowed."}, status=status.HTTP_403_FORBIDDEN)
        if lr.status != LeaveRequest.Status.PENDING_PVC:
            return Response({"detail": f"Cannot approve in status {lr.status}."}, status=status.HTTP_400_BAD_REQUEST)

        lr.status = LeaveRequest.Status.PENDING_ADMIN
        lr.pvc_officer = request.user
        lr.save(update_fields=["status", "pvc_officer"])
        self.audit_log("UPDATE", lr, {"field": "status", "to": "PENDING_ADMIN", "pvc_officer": request.user.email})
        notify_user(lr.employee.user, key="leave_pvc_approved", context={"message": "Leave approved by PVC.", "leave_id": lr.id}, title="Leave Update")
        return Response({"detail": "PVC approved."})

    @decorators.action(detail=True, methods=["post"])
    def approve_admin(self, request, *args, **kwargs):
        lr = self.get_object()
        allowed = allowed_roles_for(
            ApprovalProcessConfig.Process.LEAVE_ADMIN,
            default_roles=[User.Role.ADMIN_OFFICER, User.Role.SYSTEM_ADMIN],
        )
        if request.user.role not in allowed:
            return Response({"detail": "Not allowed."}, status=status.HTTP_403_FORBIDDEN)
        if lr.status != LeaveRequest.Status.PENDING_ADMIN:
            return Response({"detail": f"Cannot approve in status {lr.status}."}, status=status.HTTP_400_BAD_REQUEST)

        lr.status = LeaveRequest.Status.PENDING_FINANCE
        lr.admin_officer = request.user
        lr.save(update_fields=["status", "admin_officer"])
        self.audit_log("UPDATE", lr, {"field": "status", "to": "PENDING_FINANCE", "admin_officer": request.user.email})
        notify_user(lr.employee.user, key="leave_admin_approved", context={"message": "Leave approved by Administration.", "leave_id": lr.id}, title="Leave Update")
        return Response({"detail": "Admin approved."})

    @decorators.action(detail=True, methods=["post"])
    def approve_finance(self, request, *args, **kwargs):
        lr = self.get_object()
        allowed = allowed_roles_for(
            ApprovalProcessConfig.Process.LEAVE_FINANCE,
            default_roles=[User.Role.FINANCE_OFFICER, User.Role.SYSTEM_ADMIN],
        )
        if request.user.role not in allowed:
            return Response({"detail": "Not allowed."}, status=status.HTTP_403_FORBIDDEN)
        if lr.status != LeaveRequest.Status.PENDING_FINANCE:
            return Response({"detail": f"Cannot approve in status {lr.status}."}, status=status.HTTP_400_BAD_REQUEST)

        # Deduct leave balance on final approval
        year = lr.start_date.year
        balance, _ = LeaveBalance.objects.get_or_create(
            employee=lr.employee,
            leave_type=lr.leave_type,
            year=year,
            defaults={"days_entitled": lr.leave_type.default_days_per_year, "days_used": 0},
        )
        if balance.days_remaining < lr.days_requested:
            return Response(
                {"detail": "Insufficient leave balance.", "days_remaining": balance.days_remaining, "days_requested": lr.days_requested},
                status=status.HTTP_400_BAD_REQUEST,
            )
        balance.days_used = balance.days_used + lr.days_requested
        balance.save(update_fields=["days_used"])

        lr.status = LeaveRequest.Status.APPROVED
        lr.finance_officer = request.user
        lr.approved_at = timezone.now()
        lr.save(update_fields=["status", "finance_officer", "approved_at"])
        self.audit_log("UPDATE", lr, {"field": "status", "to": "APPROVED", "finance_officer": request.user.email})
        notify_user(lr.employee.user, key="leave_approved", context={"message": "Leave fully approved.", "leave_id": lr.id}, title="Leave Approved")

        accounts_email = getattr(settings, "ACCOUNTS_EMAIL", "alvinchipmunk532@gmail.com")
        send_email_message(
            accounts_email,
            subject=f"Leave Approved: {lr.employee.employee_number}",
            body=f"Leave approved for {lr.employee.user.full_name} ({lr.employee.employee_number})\nDates: {lr.start_date} to {lr.end_date}\nDays: {lr.days_requested}",
        )

        return Response({"detail": "Finance approved. Leave fully approved."})

    @decorators.action(detail=True, methods=["post"])
    def reject(self, request, *args, **kwargs):
        lr = self.get_object()
        note = request.data.get("decision_note", "")
        # Union of stage approvers
        lm_roles = allowed_roles_for(ApprovalProcessConfig.Process.LEAVE_LINE_MANAGER, [User.Role.LINE_MANAGER, User.Role.SYSTEM_ADMIN])
        hr_roles = allowed_roles_for(ApprovalProcessConfig.Process.LEAVE_HR, [User.Role.HR_MANAGER, User.Role.HR_OFFICER, User.Role.SYSTEM_ADMIN])
        pvc_roles = allowed_roles_for(ApprovalProcessConfig.Process.LEAVE_PVC, [User.Role.PVC, User.Role.SYSTEM_ADMIN])
        admin_roles = allowed_roles_for(ApprovalProcessConfig.Process.LEAVE_ADMIN, [User.Role.ADMIN_OFFICER, User.Role.SYSTEM_ADMIN])
        fin_roles = allowed_roles_for(ApprovalProcessConfig.Process.LEAVE_FINANCE, [User.Role.FINANCE_OFFICER, User.Role.SYSTEM_ADMIN])
        allowed = set(lm_roles + hr_roles + pvc_roles + admin_roles + fin_roles + [User.Role.SYSTEM_ADMIN])

        if request.user.role not in allowed:
            return Response({"detail": "Not allowed."}, status=status.HTTP_403_FORBIDDEN)

        if lr.status == LeaveRequest.Status.APPROVED:
            return Response({"detail": "Cannot reject after approval."}, status=status.HTTP_400_BAD_REQUEST)

        lr.status = LeaveRequest.Status.REJECTED
        lr.decision_note = note
        lr.save(update_fields=["status", "decision_note"])
        self.audit_log("UPDATE", lr, {"field": "status", "to": "REJECTED", "note": note})
        notify_user(lr.employee.user, key="leave_rejected", context={"message": f"Leave rejected. {note}", "leave_id": lr.id}, title="Leave Rejected")
        return Response({"detail": "Rejected."})


class PublicHolidayViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = PublicHoliday.objects.all().order_by("date")
    serializer_class = PublicHolidaySerializer
    allowed_roles = [User.Role.SYSTEM_ADMIN, User.Role.HR_MANAGER, User.Role.HR_OFFICER]
    permission_classes = [permissions.IsAuthenticated, RolePermission]
