from datetime import date

from django.db import models
from django.conf import settings
from django.utils import timezone

from accounts.fields import EncryptedTextField


class ContractType(models.TextChoices):
    PERMANENT = "PERMANENT", "Permanent"
    FIXED_TERM = "FIXED_TERM", "Fixed Term"
    PART_TIME = "PART_TIME", "Part time"
    CASUAL = "CASUAL", "Casual"
    CONSULTANCY = "CONSULTANCY", "Consultancy"
    

class Title(models.TextChoices):
    MR = "MR", "Mr"
    MS = "MS", "Ms"
    MRS = "MRS", "Mrs"
    DR = "DR", "Dr"
    PROF = "PROF", "Prof"
    REV = "REV", "Rev"


class Gender(models.TextChoices):
    MALE = "MALE", "Male"
    FEMALE = "FEMALE", "Female"
    OTHER = "OTHER", "Other"


class Department(models.Model):
    name = models.CharField(max_length=120, unique=True)
    code = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.name


class Position(models.Model):
    title = models.CharField(max_length=120)
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name="positions")
    is_academic = models.BooleanField(default=True)

    class Meta:
        unique_together = ("title", "department")

    def __str__(self):
        return f"{self.title} ({self.department.name})"


class Employee(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="employee_profile")
    employee_number = models.CharField(max_length=30, unique=True)
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name="employees")
    position = models.ForeignKey(Position, on_delete=models.PROTECT, related_name="employees")
    employment_status = models.CharField(max_length=40, default="ACTIVE")
    contract_type = models.CharField(
        max_length=40,
        choices=ContractType.choices,
        default=ContractType.PERMANENT,
    )
    hire_date = models.DateField(null=True, blank=True)

    date_of_birth = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    retirement_date = models.DateField(null=True, blank=True)
    line_manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="managed_employees",
    )

    # Basic personal details
    title = models.CharField(max_length=20, choices=Title.choices, blank=True, null=True)
    gender = models.CharField(max_length=20, choices=Gender.choices, blank=True, null=True)
    grade = models.CharField(max_length=50, blank=True, null=True)
    school = models.CharField(max_length=120, blank=True, null=True)
    
    national_id = EncryptedTextField(blank=True, null=True)
    phone = EncryptedTextField(blank=True, null=True)
    address = EncryptedTextField(blank=True, null=True)

    def __str__(self):
        return f"{self.employee_number} - {self.user.full_name}"

    def save(self, *args, **kwargs):
        creating = self._state.adding
        old = None
        if not creating and self.pk:
            old = Employee.objects.filter(pk=self.pk).only(
                "department_id", "position_id", "employment_status", "contract_type", "hire_date"
            ).first()
        super().save(*args, **kwargs)

        # Maintain employment history (best-effort; never block save)
        try:
            if creating:
                EmploymentHistory.objects.create(
                    employee=self,
                    department=self.department,
                    position=self.position,
                    employment_status=self.employment_status,
                    contract_type=self.contract_type,
                    start_date=self.hire_date or timezone.now().date(),
                )
            else:
                if old and (
                    old.department_id != self.department_id
                    or old.position_id != self.position_id
                    or old.employment_status != self.employment_status
                    or old.contract_type != self.contract_type
                ):
                    current = EmploymentHistory.objects.filter(employee=self, end_date__isnull=True).order_by("-start_date").first()
                    if current:
                        current.end_date = timezone.now().date()
                        current.save(update_fields=["end_date"])
                    EmploymentHistory.objects.create(
                        employee=self,
                        department=self.department,
                        position=self.position,
                        employment_status=self.employment_status,
                        contract_type=self.contract_type,
                        start_date=timezone.now().date(),
                    )
        except Exception:
            pass


class EmploymentHistory(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="employment_history")
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name="employment_history")
    position = models.ForeignKey(Position, on_delete=models.PROTECT, related_name="employment_history")
    employment_status = models.CharField(max_length=40)
    contract_type = models.CharField(
        max_length=40,
        choices=ContractType.choices,
    )
    start_date = models.DateField(default=date.today)
    end_date = models.DateField(null=True, blank=True)
    note = models.TextField(blank=True)

    class Meta:
        ordering = ["-start_date", "-id"]

    def __str__(self):
        return f"{self.employee.employee_number} {self.start_date}"


class Qualification(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="qualifications")
    name = models.CharField(max_length=120)
    institution = models.CharField(max_length=120, blank=True)
    year_obtained = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.employee.employee_number})"


class EmployeeDocument(models.Model):
    class Category(models.TextChoices):
        NATIONAL_ID_OR_PASSPORT = "NATIONAL_ID_OR_PASSPORT", "National ID/Passport"
        ACADEMIC_CERTIFICATES = "ACADEMIC_CERTIFICATES", "Academic Certificates"
        PROFESSIONAL_CERTIFICATIONS = "PROFESSIONAL_CERTIFICATIONS", "Professional Certifications"
        CV = "CV", "CV"
        BANKING_DETAILS = "BANKING_DETAILS", "Banking Details"
        OTHER = "OTHER", "Other"

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="documents")

    # ✅ add default so makemigrations never prompts
    category = models.CharField(
        max_length=60,
        choices=Category.choices,
        default=Category.CV,
    )

    # keep name as encrypted_file (migration will rename from file → encrypted_file)
    encrypted_file = models.FileField(upload_to="employee_documents/")

    # ✅ make these non-interactive-safe
    original_name = models.CharField(max_length=255, blank=True, default="")
    content_type = models.CharField(max_length=120, blank=True, default="")
    size_bytes = models.PositiveBigIntegerField(default=0)

    version = models.PositiveIntegerField(default=1)
    is_latest = models.BooleanField(default=True)

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"{self.category} - {self.employee.employee_number}"
