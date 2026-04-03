from django.conf import settings
from django.db import models


class ApprovalProcessConfig(models.Model):
    class Process(models.TextChoices):
        LEAVE_LINE_MANAGER = "LEAVE_LINE_MANAGER", "Leave: Line Manager Approval"
        LEAVE_HR = "LEAVE_HR", "Leave: HR Approval"
        LEAVE_PVC = "LEAVE_PVC", "Leave: PVC Approval"
        LEAVE_ADMIN = "LEAVE_ADMIN", "Leave: Admin Approval"
        LEAVE_FINANCE = "LEAVE_FINANCE", "Leave: Finance Approval"

        EDUCATION_CLAIM_HR = "EDUCATION_CLAIM_HR", "Education Assistance: HR Approval"
        EDUCATION_CLAIM_FINANCE = "EDUCATION_CLAIM_FINANCE", "Education Assistance: Finance Payment"

        VACANCY_APPROVAL = "VACANCY_APPROVAL", "Recruitment: Vacancy Approval"
        VACANCY_PUBLISH = "VACANCY_PUBLISH", "Recruitment: Vacancy Publish"

    process_code = models.CharField(max_length=40, choices=Process.choices, unique=True)
    name = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    allowed_roles = models.JSONField(default=list, blank=True)  # list of accounts.models.User.Role values
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Policy(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    document = models.FileField(upload_to="governance/policies/", blank=True, null=True)
    version = models.CharField(max_length=30, blank=True)
    effective_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "policies"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class PolicyAcknowledgement(models.Model):
    policy = models.ForeignKey(Policy, on_delete=models.CASCADE, related_name="acknowledgements")
    employee = models.ForeignKey("employees.Employee", on_delete=models.CASCADE, related_name="policy_acknowledgements")
    acknowledged_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-acknowledged_at"]
        unique_together = [("policy", "employee")]

    def __str__(self):
        return f"{self.employee} — {self.policy}"


class DisciplinaryCase(models.Model):
    employee = models.ForeignKey("employees.Employee", on_delete=models.CASCADE, related_name="disciplinary_cases")
    case_description = models.TextField()
    date = models.DateField()
    outcome = models.TextField(blank=True)
    supporting_document = models.FileField(upload_to="governance/disciplinary/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="created_disciplinary_cases",
    )

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"Case #{self.pk} — {self.employee}"


class Grievance(models.Model):
    class Status(models.TextChoices):
        OPEN = "OPEN", "Open"
        UNDER_REVIEW = "UNDER_REVIEW", "Under Review"
        RESOLVED = "RESOLVED", "Resolved"
        CLOSED = "CLOSED", "Closed"

    employee = models.ForeignKey("employees.Employee", on_delete=models.CASCADE, related_name="grievances")
    subject = models.CharField(max_length=200)
    description = models.TextField()
    date_filed = models.DateField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    resolution = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date_filed"]

    def __str__(self):
        return f"{self.subject} — {self.employee}"


class ComplianceItem(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        COMPLIANT = "COMPLIANT", "Compliant"
        NON_COMPLIANT = "NON_COMPLIANT", "Non-Compliant"

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=100, blank=True)
    due_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
