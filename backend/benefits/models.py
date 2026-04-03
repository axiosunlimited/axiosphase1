from __future__ import annotations

from django.db import models
from django.conf import settings
from django.utils import timezone

from employees.models import Employee, ContractType


class EducationAssistancePolicy(models.Model):
    """Configurable policy settings for Education Assistance module."""

    class Frequency(models.TextChoices):
        TERM = "TERM", "Per Term"
        SEMESTER = "SEMESTER", "Per Semester"
        YEAR = "YEAR", "Per Year"

    max_children_per_employee = models.PositiveIntegerField(default=2)
    allowed_levels = models.JSONField(default=list, blank=True)  # ["PRIMARY", "SECONDARY", "TERTIARY"]
    max_claim_amount_per_child = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    frequency = models.CharField(max_length=20, choices=Frequency.choices, default=Frequency.TERM)

    eligible_contract_types = models.JSONField(default=list, blank=True)  # e.g. ["PERMANENT"]
    require_completed_probation = models.BooleanField(default=False)
    max_child_age = models.PositiveIntegerField(null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Education Assistance Policy"
        verbose_name_plural = "Education Assistance Policies"

    def __str__(self):
        return f"Education Assistance Policy ({self.id})"

    @staticmethod
    def active() -> "EducationAssistancePolicy":
        obj = EducationAssistancePolicy.objects.order_by("-updated_at").first()
        if obj:
            return obj
        return EducationAssistancePolicy.objects.create(
            max_children_per_employee=2,
            allowed_levels=["PRIMARY", "SECONDARY", "TERTIARY"],
            eligible_contract_types=[ContractType.PERMANENT],
            require_completed_probation=False,
        )


class Dependant(models.Model):
    class Relationship(models.TextChoices):
        CHILD = "CHILD", "Child"
        SPOUSE = "SPOUSE", "Spouse"
        FATHER = "FATHER", "Father"
        MOTHER = "MOTHER", "Mother"
        OTHER = "OTHER", "Other"

    class EducationLevel(models.TextChoices):
        PRIMARY = "PRIMARY", "Primary"
        SECONDARY = "SECONDARY", "Secondary"
        TERTIARY = "TERTIARY", "Tertiary"

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="dependants")
    name = models.CharField(max_length=160)
    date_of_birth = models.DateField()
    relationship = models.CharField(max_length=20, choices=Relationship.choices, default=Relationship.CHILD)
    education_level = models.CharField(max_length=20, choices=EducationLevel.choices, default=EducationLevel.PRIMARY)
    institution_name = models.CharField(max_length=160, blank=True)
    student_number = models.CharField(max_length=80, blank=True)

    benefit_eligible = models.BooleanField(default=True)
    ineligible_reason = models.CharField(max_length=200, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["employee", "name"]

    def __str__(self):
        return f"{self.name} ({self.employee.employee_number})"


class DependantDocument(models.Model):
    class DocType(models.TextChoices):
        BIRTH_CERTIFICATE = "BIRTH_CERTIFICATE", "Birth certificate"
        OTHER = "OTHER", "Other"

    dependant = models.ForeignKey(Dependant, on_delete=models.CASCADE, related_name="documents")
    doc_type = models.CharField(max_length=40, choices=DocType.choices)

    encrypted_file = models.FileField(upload_to="benefits/dependants/")
    original_name = models.CharField(max_length=255)
    content_type = models.CharField(max_length=120, blank=True)
    size_bytes = models.PositiveBigIntegerField(default=0)

    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]


class EducationClaim(models.Model):
    class PeriodType(models.TextChoices):
        TERM = "TERM", "Term"
        SEMESTER = "SEMESTER", "Semester"
        YEAR = "YEAR", "Year"

    class Status(models.TextChoices):
        SUBMITTED = "SUBMITTED", "Submitted"
        NEEDS_INFO = "NEEDS_INFO", "Needs additional documents"
        HR_REJECTED = "HR_REJECTED", "Rejected by HR"
        FINANCE_PENDING = "FINANCE_PENDING", "Pending Accounts/Finance"
        PAID = "PAID", "Paid"

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="education_claims")
    dependant = models.ForeignKey(Dependant, on_delete=models.PROTECT, related_name="education_claims")

    academic_year = models.PositiveIntegerField()
    period_type = models.CharField(max_length=20, choices=PeriodType.choices)
    period_label = models.CharField(max_length=40)  # e.g., Term 1, Semester 2

    institution_name = models.CharField(max_length=160)
    amount_claimed = models.DecimalField(max_digits=12, decimal_places=2)
    amount_approved = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SUBMITTED)

    hr_reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="hr_reviewed_education_claims")
    hr_reviewed_at = models.DateTimeField(null=True, blank=True)
    hr_note = models.TextField(blank=True)

    finance_processed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="finance_processed_education_claims")
    finance_processed_at = models.DateTimeField(null=True, blank=True)
    payment_reference = models.CharField(max_length=120, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["dependant", "academic_year", "period_type", "period_label"], name="uniq_claim_child_period"),
        ]

    def __str__(self):
        return f"Claim {self.employee.employee_number} {self.academic_year} {self.period_type} {self.period_label}"


class EducationClaimDocument(models.Model):
    class DocType(models.TextChoices):
        INVOICE = "INVOICE", "Invoice/Receipt"
        REGISTRATION = "REGISTRATION", "Proof of registration"
        PAYMENT_PROOF = "PAYMENT_PROOF", "Proof of payment"
        OTHER = "OTHER", "Other"

    claim = models.ForeignKey(EducationClaim, on_delete=models.CASCADE, related_name="documents")
    doc_type = models.CharField(max_length=40, choices=DocType.choices)

    encrypted_file = models.FileField(upload_to="benefits/claims/")
    original_name = models.CharField(max_length=255)
    content_type = models.CharField(max_length=120, blank=True)
    size_bytes = models.PositiveBigIntegerField(default=0)

    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]
