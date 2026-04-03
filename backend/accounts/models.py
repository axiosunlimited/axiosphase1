from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
from .fields import EncryptedTextField
from django.conf import settings

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("role", User.Role.SYSTEM_ADMIN)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email=email, password=password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        SYSTEM_ADMIN = "SYSTEM_ADMIN", "System Administrator"
        HR_MANAGER = "HR_MANAGER", "HR Manager"
        HR_OFFICER = "HR_OFFICER", "HR Officer"
        LINE_MANAGER = "LINE_MANAGER", "Line Manager"
        PVC = "PVC", "Pro Vice Chancellor"
        ADMIN_OFFICER = "ADMIN_OFFICER", "Administration Officer"
        FINANCE_OFFICER = "FINANCE_OFFICER", "Finance Officer"
        EMPLOYEE = "EMPLOYEE", "Employee"

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=80, blank=True)
    last_name = models.CharField(max_length=80, blank=True)
    role = models.CharField(max_length=32, choices=Role.choices, default=Role.EMPLOYEE)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    # 2FA fields
    twofa_enabled = models.BooleanField(default=False)
    twofa_secret = EncryptedTextField(blank=True, null=True)
    backup_codes = models.JSONField(default=list, blank=True)  # list of hashed codes
    failed_login_attempts = models.PositiveIntegerField(default=0)
    locked_until = models.DateTimeField(blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        name = f"{self.first_name} {self.last_name}".strip()
        return name or self.email


class UserInvite(models.Model):
    """Invite flow for creating/activating users.

    Stores ONLY a SHA-256 hash of the invite token (never the raw token).
    """

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        USED = "used", "Used"
        EXPIRED = "expired", "Expired"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="invites")
    email = models.EmailField(db_index=True)
    role = models.CharField(max_length=32, choices=User.Role.choices, default=User.Role.EMPLOYEE)
    auto_activate = models.BooleanField(default=False)

    token_hash = models.CharField(max_length=64, unique=True, db_index=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_invites",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Invite<{self.email}> {self.status}"

    @property
    def is_used(self):
        return self.used_at is not None

    @property
    def is_expired(self):
        return timezone.now() >= self.expires_at

    @property
    def status(self):
        if self.is_used:
            return self.Status.USED
        if self.is_expired:
            return self.Status.EXPIRED
        return self.Status.PENDING
