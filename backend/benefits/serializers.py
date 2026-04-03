from __future__ import annotations

from rest_framework import serializers
from django.utils import timezone
from django.core.files.base import ContentFile
from django.db import models
import uuid

from employees.models import Employee
from employees.serializers import EmployeeMiniSerializer

from config.crypto import encrypt_bytes

from .models import (
    EducationAssistancePolicy,
    Dependant,
    DependantDocument,
    EducationClaim,
    EducationClaimDocument,
)
from .services import recalc_dependant_eligibility, approved_claims_for_employee_in_period


class EducationAssistancePolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = EducationAssistancePolicy
        fields = [
            "id",
            "max_children_per_employee",
            "allowed_levels",
            "max_claim_amount_per_child",
            "frequency",
            "eligible_contract_types",
            "require_completed_probation",
            "max_child_age",
            "updated_at",
        ]
        read_only_fields = ["updated_at"]


class DependantSerializer(serializers.ModelSerializer):
    employee = EmployeeMiniSerializer(read_only=True)
    employee_id = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all(), source="employee", write_only=True, required=False)

    class Meta:
        model = Dependant
        fields = [
            "id",
            "employee",
            "employee_id",
            "name",
            "date_of_birth",
            "relationship",
            "education_level",
            "institution_name",
            "student_number",
            "benefit_eligible",
            "ineligible_reason",
            "created_at",
        ]
        read_only_fields = ["benefit_eligible", "ineligible_reason", "created_at"]

    def create(self, validated_data):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if user and getattr(user, "role", None) == "EMPLOYEE":
            emp = getattr(user, "employee_profile", None)
            if not emp:
                raise serializers.ValidationError({"detail": "Employee profile missing. Please contact HR to create your record."})
            validated_data["employee"] = emp
        obj = super().create(validated_data)
        recalc_dependant_eligibility(obj.employee)
        return obj

    def update(self, instance, validated_data):
        obj = super().update(instance, validated_data)
        recalc_dependant_eligibility(obj.employee)
        return obj


class DependantDocumentSerializer(serializers.ModelSerializer):
    file = serializers.FileField(write_only=True, required=True)

    class Meta:
        model = DependantDocument
        fields = [
            "id",
            "dependant",
            "doc_type",
            "file",
            "original_name",
            "content_type",
            "size_bytes",
            "uploaded_by",
            "uploaded_at",
        ]
        read_only_fields = ["original_name", "content_type", "size_bytes", "uploaded_by", "uploaded_at"]

    def create(self, validated_data):
        upload = validated_data.pop("file")
        raw = upload.read()
        encrypted = encrypt_bytes(raw)

        name = f"{uuid.uuid4().hex}.enc"
        validated_data["original_name"] = upload.name
        validated_data["content_type"] = getattr(upload, "content_type", "") or ""
        validated_data["size_bytes"] = getattr(upload, "size", 0) or len(raw)
        request = self.context.get("request")
        validated_data["uploaded_by"] = getattr(request, "user", None)

        obj = DependantDocument(**validated_data)
        obj.encrypted_file.save(name, ContentFile(encrypted), save=False)
        obj.save()
        return obj

    def validate_file(self, f):
        """Enforce file size/type restrictions aligned with system document settings."""
        from pathlib import Path
        from django.conf import settings
        from system.models import SystemSetting

        max_mb = getattr(settings, "DOCUMENTS_MAX_FILE_SIZE_MB", 10)
        override = SystemSetting.get_value("documents.max_file_size_mb")
        try:
            if override is not None:
                max_mb = int(override if not isinstance(override, dict) else override.get("value"))
        except Exception:
            pass
        max_bytes = int(max_mb) * 1024 * 1024
        if getattr(f, "size", 0) and f.size > max_bytes:
            raise serializers.ValidationError(f"File too large. Max {max_mb} MB.")

        allowed_exts = getattr(settings, "DOCUMENTS_ALLOWED_EXTENSIONS", ["pdf", "doc", "docx", "jpg", "jpeg", "png", "gif", "bmp", "webp", "img", "tiff", "txt", "xlsx", "xls", "csv", "pptx", "ppt"])
        norm = []
        for e in allowed_exts:
            e = (e or "").lower().strip()
            if not e:
                continue
            norm.append(e if e.startswith(".") else f".{e}")
        ext = Path(f.name or "").suffix.lower()
        if ext not in norm:
            raise serializers.ValidationError("Unsupported file type.")
        return f


class EducationClaimDocumentSerializer(serializers.ModelSerializer):
    file = serializers.FileField(write_only=True, required=True)

    class Meta:
        model = EducationClaimDocument
        fields = [
            "id",
            "claim",
            "doc_type",
            "file",
            "original_name",
            "content_type",
            "size_bytes",
            "uploaded_by",
            "uploaded_at",
        ]
        read_only_fields = ["original_name", "content_type", "size_bytes", "uploaded_by", "uploaded_at"]

    def create(self, validated_data):
        upload = validated_data.pop("file")
        raw = upload.read()
        encrypted = encrypt_bytes(raw)

        name = f"{uuid.uuid4().hex}.enc"
        validated_data["original_name"] = upload.name
        validated_data["content_type"] = getattr(upload, "content_type", "") or ""
        validated_data["size_bytes"] = getattr(upload, "size", 0) or len(raw)
        request = self.context.get("request")
        validated_data["uploaded_by"] = getattr(request, "user", None)

        obj = EducationClaimDocument(**validated_data)
        obj.encrypted_file.save(name, ContentFile(encrypted), save=False)
        obj.save()
        return obj

    def validate_file(self, f):
        from pathlib import Path
        from django.conf import settings
        from system.models import SystemSetting

        max_mb = getattr(settings, "DOCUMENTS_MAX_FILE_SIZE_MB", 10)
        override = SystemSetting.get_value("documents.max_file_size_mb")
        try:
            if override is not None:
                max_mb = int(override if not isinstance(override, dict) else override.get("value"))
        except Exception:
            pass
        max_bytes = int(max_mb) * 1024 * 1024
        if getattr(f, "size", 0) and f.size > max_bytes:
            raise serializers.ValidationError(f"File too large. Max {max_mb} MB.")

        allowed_exts = getattr(settings, "DOCUMENTS_ALLOWED_EXTENSIONS", ["pdf", "doc", "docx", "jpg", "jpeg", "png", "gif", "bmp", "webp", "img", "tiff", "txt", "xlsx", "xls", "csv", "pptx", "ppt"])
        norm = []
        for e in allowed_exts:
            e = (e or "").lower().strip()
            if not e:
                continue
            norm.append(e if e.startswith(".") else f".{e}")
        ext = Path(f.name or "").suffix.lower()
        if ext not in norm:
            raise serializers.ValidationError("Unsupported file type.")
        return f


class EducationClaimSerializer(serializers.ModelSerializer):
    employee = EmployeeMiniSerializer(read_only=True)
    dependant_name = serializers.CharField(source="dependant.name", read_only=True)

    class Meta:
        model = EducationClaim
        fields = [
            "id",
            "employee",
            "dependant",
            "dependant_name",
            "academic_year",
            "period_type",
            "period_label",
            "institution_name",
            "amount_claimed",
            "amount_approved",
            "status",
            "hr_note",
            "payment_reference",
            "created_at",
        ]
        read_only_fields = ["amount_approved", "status", "hr_note", "payment_reference", "created_at"]

    def validate(self, attrs):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        emp = getattr(user, "employee_profile", None)

        policy = EducationAssistancePolicy.active()

        dependant = attrs.get("dependant")
        if dependant and emp and dependant.employee_id != emp.id and getattr(user, "role", "") == "EMPLOYEE":
            raise serializers.ValidationError({"dependant": "Invalid dependant"})

        if dependant and not dependant.benefit_eligible:
            raise serializers.ValidationError({"dependant": dependant.ineligible_reason or "Dependant not eligible"})

        # Employment eligibility (contract type / probation)
        if emp:
            # Prefer active contract record (if present), otherwise fall back to Employee.contract_type.
            active_contract_type = (emp.contract_type or "")
            probation_end = None
            try:
                from contracts.models import Contract
                today = timezone.now().date()
                c = (
                    Contract.objects.filter(employee=emp, start_date__lte=today)
                    .filter(models.Q(end_date__isnull=True) | models.Q(end_date__gte=today))
                    .order_by("-start_date", "-id")
                    .first()
                )
                if c:
                    active_contract_type = c.contract_type or active_contract_type
                    probation_end = c.probation_end_date
            except Exception:
                c = None

            if policy.eligible_contract_types:
                if (active_contract_type or "").upper() not in [x.upper() for x in policy.eligible_contract_types]:
                    raise serializers.ValidationError({"detail": "Employee not eligible for education assistance (contract type)."})

            if policy.require_completed_probation and probation_end:
                if timezone.now().date() < probation_end:
                    raise serializers.ValidationError({"detail": "Employee not eligible: probation not completed."})

        # Limit approved claims per period per employee
        academic_year = attrs.get("academic_year")
        period_type = attrs.get("period_type")
        period_label = attrs.get("period_label")
        if emp and academic_year and period_type and period_label:
            approved_count = approved_claims_for_employee_in_period(emp, academic_year, period_type, period_label)
            if approved_count >= (policy.max_children_per_employee or 2):
                raise serializers.ValidationError({"detail": f"Policy limit exceeded: max {policy.max_children_per_employee} approved claims per period."})

        # Max claim amount
        if policy.max_claim_amount_per_child is not None:
            amt = attrs.get("amount_claimed")
            if amt and amt > policy.max_claim_amount_per_child:
                raise serializers.ValidationError({"amount_claimed": "Amount exceeds policy maximum per child."})

        # Allowed level
        if dependant and policy.allowed_levels:
            if dependant.education_level not in policy.allowed_levels:
                raise serializers.ValidationError({"dependant": "Dependant level not covered by policy."})

        return attrs

    def create(self, validated_data):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if user and getattr(user, "role", None) == "EMPLOYEE":
            emp = getattr(user, "employee_profile", None)
            if not emp:
                raise serializers.ValidationError({"detail": "Employee profile missing"})
            validated_data["employee"] = emp
        return super().create(validated_data)
