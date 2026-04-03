from __future__ import annotations

from rest_framework import viewsets, permissions, decorators, status
from rest_framework.response import Response
from django.http import FileResponse, HttpResponse
from django.utils import timezone
from io import BytesIO

from accounts.models import User
from accounts.permissions import RolePermission
from audit.mixins import AuditMixin

from config.crypto import decrypt_bytes

from .models import (
    EducationAssistancePolicy,
    Dependant,
    DependantDocument,
    EducationClaim,
    EducationClaimDocument,
)
from .serializers import (
    EducationAssistancePolicySerializer,
    DependantSerializer,
    DependantDocumentSerializer,
    EducationClaimSerializer,
    EducationClaimDocumentSerializer,
)
from .services import recalc_dependant_eligibility

from notifications.utils import notify_user


class EducationAssistancePolicyViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = EducationAssistancePolicy.objects.all()
    serializer_class = EducationAssistancePolicySerializer
    allowed_roles = [User.Role.SYSTEM_ADMIN, User.Role.HR_MANAGER, User.Role.HR_OFFICER]
    permission_classes = [permissions.IsAuthenticated, RolePermission]

    @decorators.action(detail=False, methods=["get"], url_path="active")
    def active(self, request, *args, **kwargs):
        policy = EducationAssistancePolicy.active()
        return Response(EducationAssistancePolicySerializer(policy).data)


class DependantViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = Dependant.objects.select_related("employee", "employee__user").all()
    serializer_class = DependantSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        if user.role == User.Role.EMPLOYEE:
            emp = getattr(user, "employee_profile", None)
            return qs.filter(employee=emp) if emp else qs.none()
        if user.role == User.Role.LINE_MANAGER:
            return qs.none()
        if user.role in [User.Role.SYSTEM_ADMIN, User.Role.HR_MANAGER, User.Role.HR_OFFICER]:
            return qs
        return qs.none()

    def get_permissions(self):
        if self.request.method in ("POST", "PUT", "PATCH", "DELETE"):
            # Employees can manage their own dependants; HR/Admin can manage all.
            self.allowed_roles = [User.Role.SYSTEM_ADMIN, User.Role.HR_MANAGER, User.Role.HR_OFFICER, User.Role.EMPLOYEE]
            return [permissions.IsAuthenticated(), RolePermission()]
        return [permissions.IsAuthenticated()]

    def perform_destroy(self, instance):
        employee = instance.employee
        super().perform_destroy(instance)
        recalc_dependant_eligibility(employee)


class DependantDocumentViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = DependantDocument.objects.select_related("dependant", "dependant__employee", "dependant__employee__user").all()
    serializer_class = DependantDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        if user.role == User.Role.EMPLOYEE:
            emp = getattr(user, "employee_profile", None)
            return qs.filter(dependant__employee=emp) if emp else qs.none()
        if user.role == User.Role.LINE_MANAGER:
            return qs.none()
        if user.role in [User.Role.SYSTEM_ADMIN, User.Role.HR_MANAGER, User.Role.HR_OFFICER]:
            return qs
        return qs.none()

    def get_permissions(self):
        if self.request.method in ("POST", "PUT", "PATCH", "DELETE"):
            self.allowed_roles = [User.Role.SYSTEM_ADMIN, User.Role.HR_MANAGER, User.Role.HR_OFFICER, User.Role.EMPLOYEE]
            return [permissions.IsAuthenticated(), RolePermission()]
        return [permissions.IsAuthenticated()]

    @decorators.action(detail=True, methods=["get"])
    def download(self, request, pk=None, *args, **kwargs):
        obj = self.get_object()
        # Employees can download their own dependant docs; HR/Admin can download all.
        if request.user.role == User.Role.EMPLOYEE:
            emp = getattr(request.user, "employee_profile", None)
            if not emp or obj.dependant.employee_id != emp.id:
                return Response({"detail": "Not allowed."}, status=status.HTTP_403_FORBIDDEN)
        elif request.user.role not in [User.Role.SYSTEM_ADMIN, User.Role.HR_MANAGER, User.Role.HR_OFFICER]:
            return Response({"detail": "Not allowed."}, status=status.HTTP_403_FORBIDDEN)

        raw = obj.encrypted_file.open("rb").read()
        data = decrypt_bytes(raw)
        self.audit_log("READ", obj, {"info": "Dependant document downloaded"})
        resp = HttpResponse(data, content_type=obj.content_type or "application/octet-stream")
        resp["Content-Disposition"] = f'attachment; filename="{obj.original_name}"'
        return resp


class EducationClaimViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = EducationClaim.objects.select_related("employee", "employee__user", "dependant").all()
    serializer_class = EducationClaimSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        if user.role == User.Role.EMPLOYEE:
            emp = getattr(user, "employee_profile", None)
            return qs.filter(employee=emp) if emp else qs.none()
        if user.role == User.Role.LINE_MANAGER:
            return qs.none()
        if user.role in [User.Role.SYSTEM_ADMIN, User.Role.HR_MANAGER, User.Role.HR_OFFICER, User.Role.FINANCE_OFFICER]:
            return qs
        return qs.none()

    def get_permissions(self):
        if self.request.method in ("POST", "PUT", "PATCH", "DELETE"):
            # Employees can submit and update their own claims; HR can manage all.
            self.allowed_roles = [User.Role.SYSTEM_ADMIN, User.Role.HR_MANAGER, User.Role.HR_OFFICER, User.Role.EMPLOYEE]
            return [permissions.IsAuthenticated(), RolePermission()]
        return [permissions.IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        # employee creates for themselves
        return super().create(request, *args, **kwargs)

    @decorators.action(detail=True, methods=["post"], url_path="hr-approve")
    def hr_approve(self, request, pk=None, *args, **kwargs):
        claim = self.get_object()
        if request.user.role not in [User.Role.SYSTEM_ADMIN, User.Role.HR_MANAGER, User.Role.HR_OFFICER]:
            return Response({"detail": "Not allowed."}, status=status.HTTP_403_FORBIDDEN)
        if claim.status not in [EducationClaim.Status.SUBMITTED, EducationClaim.Status.NEEDS_INFO]:
            return Response({"detail": f"Cannot approve in status {claim.status}"}, status=status.HTTP_400_BAD_REQUEST)

        # Validate required docs before approval.
        policy = EducationAssistancePolicy.active()
        required_claim_docs = {EducationClaimDocument.DocType.INVOICE, EducationClaimDocument.DocType.REGISTRATION}
        existing_claim_docs = set(claim.documents.values_list("doc_type", flat=True))
        missing = sorted(list(required_claim_docs - existing_claim_docs))
        if missing:
            return Response({"detail": "Missing required claim documents", "missing": missing}, status=status.HTTP_400_BAD_REQUEST)

        # Birth certificate required if not already submitted
        has_birth_cert = DependantDocument.objects.filter(
            dependant=claim.dependant,
            doc_type=DependantDocument.DocType.BIRTH_CERTIFICATE,
        ).exists()
        if not has_birth_cert:
            return Response({"detail": "Missing birth certificate for dependant."}, status=status.HTTP_400_BAD_REQUEST)

        # Enforce policy max children per period at approval time.
        max_children = policy.max_children_per_employee or 2
        approved_dependants = set(
            EducationClaim.objects.filter(
                employee=claim.employee,
                academic_year=claim.academic_year,
                period_type=claim.period_type,
                period_label=claim.period_label,
                status__in=[EducationClaim.Status.FINANCE_PENDING, EducationClaim.Status.PAID],
            ).values_list("dependant_id", flat=True)
        )
        if claim.dependant_id not in approved_dependants and len(approved_dependants) >= max_children:
            return Response(
                {"detail": f"Policy limit exceeded: max {max_children} approved claims per period."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        amt = request.data.get("amount_approved")
        note = request.data.get("hr_note", "")
        if amt is None or amt == "":
            amt = claim.amount_claimed

        try:
            amt_val = float(amt)
        except Exception:
            return Response({"detail": "amount_approved must be a number"}, status=status.HTTP_400_BAD_REQUEST)

        if amt_val < 0:
            return Response({"detail": "amount_approved must be >= 0"}, status=status.HTTP_400_BAD_REQUEST)

        if claim.amount_claimed is not None and amt_val > float(claim.amount_claimed):
            return Response({"detail": "amount_approved cannot exceed amount_claimed"}, status=status.HTTP_400_BAD_REQUEST)

        if policy.max_claim_amount_per_child is not None and amt_val > float(policy.max_claim_amount_per_child):
            return Response({"detail": "amount_approved exceeds policy maximum"}, status=status.HTTP_400_BAD_REQUEST)

        claim.amount_approved = amt
        claim.hr_note = note
        claim.status = EducationClaim.Status.FINANCE_PENDING
        claim.hr_reviewed_by = request.user
        claim.hr_reviewed_at = timezone.now()
        claim.save()

        self.audit_log("UPDATE", claim, {"status": "FINANCE_PENDING", "amount_approved": str(claim.amount_approved or "")})

        notify_user(
            claim.employee.user,
            key="education_claim_hr_approved",
            context={"claim_id": claim.id, "amount_approved": str(claim.amount_approved or ""), "note": note},
        )
        return Response({"detail": "HR approved."})

    @decorators.action(detail=True, methods=["post"], url_path="resubmit")
    def resubmit(self, request, pk=None, *args, **kwargs):
        """Employee resubmits a claim after HR requested more info."""
        claim = self.get_object()
        if request.user.role != User.Role.EMPLOYEE:
            return Response({"detail": "Not allowed."}, status=status.HTTP_403_FORBIDDEN)
        emp = getattr(request.user, "employee_profile", None)
        if not emp or claim.employee_id != emp.id:
            return Response({"detail": "Not allowed."}, status=status.HTTP_403_FORBIDDEN)
        if claim.status != EducationClaim.Status.NEEDS_INFO:
            return Response({"detail": "Can only resubmit from NEEDS_INFO."}, status=status.HTTP_400_BAD_REQUEST)

        claim.status = EducationClaim.Status.SUBMITTED
        claim.save(update_fields=["status"])
        self.audit_log("UPDATE", claim, {"status": "SUBMITTED", "info": "Employee resubmitted claim"})
        notify_user(
            request.user,
            key="education_claim_resubmitted",
            context={"claim_id": claim.id},
            title="Education claim resubmitted",
            message=f"Claim #{claim.id} was resubmitted for HR review.",
        )
        return Response({"detail": "Resubmitted."})

    @decorators.action(detail=True, methods=["post"], url_path="hr-reject")
    def hr_reject(self, request, pk=None, *args, **kwargs):
        claim = self.get_object()
        if request.user.role not in [User.Role.SYSTEM_ADMIN, User.Role.HR_MANAGER, User.Role.HR_OFFICER]:
            return Response({"detail": "Not allowed."}, status=status.HTTP_403_FORBIDDEN)
        if claim.status not in [EducationClaim.Status.SUBMITTED, EducationClaim.Status.NEEDS_INFO]:
            return Response({"detail": f"Cannot reject in status {claim.status}"}, status=status.HTTP_400_BAD_REQUEST)

        note = request.data.get("hr_note", "")
        claim.hr_note = note
        claim.status = EducationClaim.Status.HR_REJECTED
        claim.hr_reviewed_by = request.user
        claim.hr_reviewed_at = timezone.now()
        claim.save()

        notify_user(
            claim.employee.user,
            key="education_claim_hr_rejected",
            context={"claim_id": claim.id, "note": note},
        )
        return Response({"detail": "HR rejected."})

    @decorators.action(detail=True, methods=["post"], url_path="request-info")
    def request_info(self, request, pk=None, *args, **kwargs):
        claim = self.get_object()
        if request.user.role not in [User.Role.SYSTEM_ADMIN, User.Role.HR_MANAGER, User.Role.HR_OFFICER]:
            return Response({"detail": "Not allowed."}, status=status.HTTP_403_FORBIDDEN)
        if claim.status != EducationClaim.Status.SUBMITTED:
            return Response({"detail": "Can only request info from SUBMITTED."}, status=status.HTTP_400_BAD_REQUEST)

        note = request.data.get("hr_note", "")
        claim.hr_note = note
        claim.status = EducationClaim.Status.NEEDS_INFO
        claim.hr_reviewed_by = request.user
        claim.hr_reviewed_at = timezone.now()
        claim.save()

        notify_user(
            claim.employee.user,
            key="education_claim_needs_info",
            context={"claim_id": claim.id, "note": note},
        )
        return Response({"detail": "Requested more info."})

    @decorators.action(detail=True, methods=["post"], url_path="finance-paid")
    def finance_paid(self, request, pk=None, *args, **kwargs):
        claim = self.get_object()
        if request.user.role not in [User.Role.SYSTEM_ADMIN, User.Role.FINANCE_OFFICER]:
            return Response({"detail": "Not allowed."}, status=status.HTTP_403_FORBIDDEN)
        if claim.status != EducationClaim.Status.FINANCE_PENDING:
            return Response({"detail": "Claim is not pending finance."}, status=status.HTTP_400_BAD_REQUEST)

        # Require proof of payment document before marking paid.
        has_payment_proof = claim.documents.filter(doc_type=EducationClaimDocument.DocType.PAYMENT_PROOF).exists()
        if not has_payment_proof:
            return Response({"detail": "Missing payment proof document."}, status=status.HTTP_400_BAD_REQUEST)

        ref = request.data.get("payment_reference", "")
        claim.payment_reference = ref
        claim.status = EducationClaim.Status.PAID
        claim.finance_processed_by = request.user
        claim.finance_processed_at = timezone.now()
        claim.save()

        self.audit_log("UPDATE", claim, {"status": "PAID", "payment_reference": ref})

        notify_user(
            claim.employee.user,
            key="education_claim_paid",
            context={"claim_id": claim.id, "payment_reference": ref},
        )
        return Response({"detail": "Marked as paid."})


class EducationClaimDocumentViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = EducationClaimDocument.objects.select_related("claim", "claim__employee", "claim__employee__user").all()
    serializer_class = EducationClaimDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        if user.role == User.Role.EMPLOYEE:
            emp = getattr(user, "employee_profile", None)
            return qs.filter(claim__employee=emp) if emp else qs.none()
        if user.role == User.Role.LINE_MANAGER:
            return qs.none()
        if user.role in [User.Role.SYSTEM_ADMIN, User.Role.HR_MANAGER, User.Role.HR_OFFICER, User.Role.FINANCE_OFFICER]:
            return qs
        return qs.none()

    def get_permissions(self):
        if self.request.method in ("POST", "PUT", "PATCH", "DELETE"):
            self.allowed_roles = [User.Role.SYSTEM_ADMIN, User.Role.HR_MANAGER, User.Role.HR_OFFICER, User.Role.FINANCE_OFFICER, User.Role.EMPLOYEE]
            return [permissions.IsAuthenticated(), RolePermission()]
        return [permissions.IsAuthenticated()]

    @decorators.action(detail=True, methods=["get"])
    def download(self, request, pk=None, *args, **kwargs):
        obj = self.get_object()
        # Access: owning employee or HR/Admin/Finance.
        if request.user.role == User.Role.EMPLOYEE:
            emp = getattr(request.user, "employee_profile", None)
            if not emp or obj.claim.employee_id != emp.id:
                return Response({"detail": "Not allowed."}, status=status.HTTP_403_FORBIDDEN)
        elif request.user.role not in [User.Role.SYSTEM_ADMIN, User.Role.HR_MANAGER, User.Role.HR_OFFICER, User.Role.FINANCE_OFFICER]:
            return Response({"detail": "Not allowed."}, status=status.HTTP_403_FORBIDDEN)

        raw = obj.encrypted_file.open("rb").read()
        data = decrypt_bytes(raw)
        self.audit_log("READ", obj, {"info": "Claim document downloaded"})
        resp = HttpResponse(data, content_type=obj.content_type or "application/octet-stream")
        resp["Content-Disposition"] = f'attachment; filename="{obj.original_name}"'
        return resp
