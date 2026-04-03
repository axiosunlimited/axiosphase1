from __future__ import annotations

from django.db import models
from django.utils import timezone

from employees.models import Employee, ContractType


class Contract(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="contracts")
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    probation_end_date = models.DateField(null=True, blank=True)
    contract_type = models.CharField(
        max_length=40,
        choices=ContractType.choices,
        default=ContractType.PERMANENT,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-start_date", "-id"]

    def __str__(self):
        return f"{self.employee.employee_number} contract {self.start_date}"

    @property
    def is_active(self) -> bool:
        if self.end_date is None:
            return True
        return self.end_date >= timezone.now().date()
