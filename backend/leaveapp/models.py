from django.db import models
from django.conf import settings
from employees.models import Employee

class LeaveType(models.Model):
    name = models.CharField(max_length=80)
    default_days_per_year = models.PositiveIntegerField(default=20)
    requires_approval = models.BooleanField(default=True)
    carry_forward_allowed = models.BooleanField(default=False)

    class Meta:
        unique_together = ("name",)

    def __str__(self):
        return self.name

class PublicHoliday(models.Model):
    date = models.DateField(unique=True)
    name = models.CharField(max_length=120)

    def __str__(self):
        return f"{self.date} - {self.name}"

class LeaveBalance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="leave_balances")
    leave_type = models.ForeignKey(LeaveType, on_delete=models.PROTECT, related_name="balances")
    year = models.PositiveIntegerField()
    days_entitled = models.PositiveIntegerField(default=0)
    days_used = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("employee", "leave_type", "year")

    @property
    def days_remaining(self):
        return max(0, self.days_entitled - self.days_used)

    def __str__(self):
        return f"{self.employee.employee_number} {self.leave_type.name} {self.year}"

class LeaveRequest(models.Model):
    class Status(models.TextChoices):
        PENDING_LM = "PENDING_LM", "Pending line manager"
        PENDING_HR = "PENDING_HR", "Pending HR"
        PENDING_PVC = "PENDING_PVC", "Pending PVC"
        PENDING_ADMIN = "PENDING_ADMIN", "Pending Admin"
        PENDING_FINANCE = "PENDING_FINANCE", "Pending Finance"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"
        CANCELLED = "CANCELLED", "Cancelled"

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="leave_requests")
    leave_type = models.ForeignKey(LeaveType, on_delete=models.PROTECT, related_name="requests")
    start_date = models.DateField()
    end_date = models.DateField()
    days_requested = models.PositiveIntegerField(default=0)

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING_LM)
    reason = models.TextField(blank=True)

    line_manager = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="lm_leave_requests")
    hr_officer = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="hr_leave_requests")
    pvc_officer = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="pvc_leave_requests")
    admin_officer = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="admin_leave_requests")
    finance_officer = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="finance_leave_requests")
    supporting_document = models.FileField(upload_to="leave_docs/", null=True, blank=True)
    decision_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Leave {self.employee.employee_number} {self.start_date} - {self.end_date}"
