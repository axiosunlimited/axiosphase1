from django.db import models
from employees.models import Department, Position, Employee


class EstablishmentItem(models.Model):
    year = models.PositiveIntegerField()
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name="establishment_items")
    position = models.ForeignKey(Position, on_delete=models.PROTECT, related_name="establishment_items")
    budgeted_headcount = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("year", "department", "position")

    def __str__(self):
        return f"{self.year} {self.department.name} {self.position.title}"


class Separation(models.Model):
    class SeparationType(models.TextChoices):
        RESIGNATION = "RESIGNATION", "Resignation"
        RETIREMENT = "RETIREMENT", "Retirement"
        TERMINATION = "TERMINATION", "Termination"
        CONTRACT_END = "CONTRACT_END", "Contract End"
        OTHER = "OTHER", "Other"

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="separations")
    separation_date = models.DateField()
    separation_type = models.CharField(max_length=20, choices=SeparationType.choices, default=SeparationType.OTHER)
    reason = models.TextField(blank=True)

    def __str__(self):
        return f"{self.employee.employee_number} - {self.separation_date}"
