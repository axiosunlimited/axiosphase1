from django.db import models
from employees.models import Department, Position

class Vacancy(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        SUBMITTED = "SUBMITTED", "Submitted"
        APPROVED = "APPROVED", "Approved"
        PUBLISHED = "PUBLISHED", "Published"
        CLOSED = "CLOSED", "Closed"

    title = models.CharField(max_length=160)
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name="vacancies")
    position = models.ForeignKey(Position, on_delete=models.PROTECT, related_name="vacancies")
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)
    closing_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} ({self.department.name})"

class Applicant(models.Model):
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE, related_name="applicants")
    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True)
    cv = models.FileField(upload_to="recruitment/cv/", blank=True, null=True)
    status = models.CharField(max_length=30, default="APPLIED")  # APPLIED/SHORTLISTED/REJECTED/OFFERED
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.vacancy.title}"

class Interview(models.Model):
    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE, related_name="interviews")
    scheduled_at = models.DateTimeField()
    location = models.CharField(max_length=160, blank=True)
    notes = models.TextField(blank=True)
    outcome = models.CharField(max_length=40, blank=True)

    def __str__(self):
        return f"Interview - {self.applicant}"

class Appointment(models.Model):
    applicant = models.OneToOneField(Applicant, on_delete=models.PROTECT, related_name="appointment")
    start_date = models.DateField()
    salary_note = models.CharField(max_length=120, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Appointment - {self.applicant}"
