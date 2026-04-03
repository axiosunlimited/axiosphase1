from django.db import models
from django.conf import settings


class ReportDefinition(models.Model):
    """A stored definition for a custom report.

    The `definition` JSON uses a safe, whitelisted query language:
    {
      "fields": ["field", "related__field"],
      "filters": [{"field": "department__id", "op": "eq", "value": 1}],
      "order_by": ["department__name", "-employee_number"],
      "group_by": ["department__name"],
      "aggregations": [{"op": "count", "field": "id", "as": "count"}],
      "limit": 1000
    }
    """

    class Dataset(models.TextChoices):
        EMPLOYEES = "EMPLOYEES", "Employees"
        EMPLOYMENT_HISTORY = "EMPLOYMENT_HISTORY", "Employment History"
        LEAVE_REQUESTS = "LEAVE_REQUESTS", "Leave Requests"
        LEAVE_BALANCES = "LEAVE_BALANCES", "Leave Balances"
        VACANCIES = "VACANCIES", "Vacancies"
        APPLICANTS = "APPLICANTS", "Applicants"
        APPRAISALS = "APPRAISALS", "Appraisals"
        TRAINING_RECORDS = "TRAINING_RECORDS", "Training Records"
        ESTABLISHMENT = "ESTABLISHMENT", "Staff Establishment"
        SEPARATIONS = "SEPARATIONS", "Separations"

    name = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    dataset = models.CharField(max_length=40, choices=Dataset.choices)
    definition = models.JSONField(default=dict, blank=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="report_definitions")
    is_system = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        unique_together = ("name", "dataset", "created_by")

    def __str__(self):
        return self.name
