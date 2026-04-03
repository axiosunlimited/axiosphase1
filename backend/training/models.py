from django.db import models
from django.conf import settings
from employees.models import Employee, Department


class Competency(models.Model):
    name = models.CharField(max_length=120, unique=True)
    category = models.CharField(max_length=120, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class EmployeeCompetency(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="competencies")
    competency = models.ForeignKey(Competency, on_delete=models.PROTECT, related_name="employee_competencies")
    level = models.PositiveSmallIntegerField(default=1)  # 1-5
    last_assessed = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ("employee", "competency")

    def __str__(self):
        return f"{self.employee.employee_number} - {self.competency.name}"


class TrainingProgram(models.Model):
    title = models.CharField(max_length=180)
    provider = models.CharField(max_length=180, blank=True)
    category = models.CharField(max_length=120, blank=True)
    description = models.TextField(blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    estimated_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return self.title


class TrainingNeed(models.Model):
    class Priority(models.TextChoices):
        LOW = "LOW", "Low"
        MEDIUM = "MEDIUM", "Medium"
        HIGH = "HIGH", "High"

    employee = models.ForeignKey(Employee, null=True, blank=True, on_delete=models.CASCADE, related_name="training_needs")
    department = models.ForeignKey(Department, null=True, blank=True, on_delete=models.PROTECT, related_name="training_needs")
    competency = models.ForeignKey(Competency, null=True, blank=True, on_delete=models.PROTECT, related_name="training_needs")

    description = models.TextField(blank=True)
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM)
    identified_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="identified_training_needs")
    identified_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        target = self.employee.employee_number if self.employee else (self.department.name if self.department else "General")
        return f"TrainingNeed({target})"


class EmployeeTraining(models.Model):
    class Status(models.TextChoices):
        PLANNED = "PLANNED", "Planned"
        ATTENDED = "ATTENDED", "Attended"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="training_records")
    program = models.ForeignKey(TrainingProgram, on_delete=models.PROTECT, related_name="enrolments")
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PLANNED)
    cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    outcome = models.TextField(blank=True)
    certificate = models.FileField(upload_to="training/certificates/", blank=True, null=True)
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="recorded_trainings")
    recorded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee.employee_number} - {self.program.title}"
