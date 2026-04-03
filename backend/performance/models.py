from django.db import models
from employees.models import Employee

class AppraisalTemplate(models.Model):
    name = models.CharField(max_length=120, unique=True)
    schema = models.JSONField(default=dict, blank=True)  # configurable form fields

    def __str__(self):
        return self.name

class Appraisal(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        SUBMITTED = "SUBMITTED", "Submitted"
        SUPERVISOR_REVIEW = "SUPERVISOR_REVIEW", "Supervisor Review"
        HR_REVIEW = "HR_REVIEW", "HR Review"
        FINALIZED = "FINALIZED", "Finalized"

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="appraisals")
    template = models.ForeignKey(AppraisalTemplate, on_delete=models.PROTECT, related_name="appraisals")
    year = models.PositiveIntegerField()
    period = models.CharField(max_length=40, default="ANNUAL")  # ANNUAL / PROBATION
    self_assessment = models.JSONField(default=dict, blank=True)
    supervisor_feedback = models.JSONField(default=dict, blank=True)
    hr_notes = models.TextField(blank=True)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("employee", "template", "year", "period")

    def __str__(self):
        return f"{self.employee.employee_number} {self.year} {self.period}"

class Goal(models.Model):
    appraisal = models.ForeignKey(Appraisal, on_delete=models.CASCADE, related_name="goals")
    description = models.CharField(max_length=255)
    progress_note = models.TextField(blank=True)

    def __str__(self):
        return self.description
