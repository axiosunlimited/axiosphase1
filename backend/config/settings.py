from pathlib import Path
import environ
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DJANGO_DEBUG=(bool, False),
)
environ.Env.read_env(str(BASE_DIR.parent / ".env"))

SECRET_KEY = env("DJANGO_SECRET_KEY", default="unsafe-dev-key")
DEBUG = env("DJANGO_DEBUG", default=True)

ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "drf_spectacular",
    "corsheaders",

    # Local
    "accounts",
    "audit",
    "employees",
    "recruitment",
    "leaveapp",
    "performance",
    "notifications",
    "training",
    "workforce",
    "governance",
    "reports",
    "evaluation",

    # Requirements doc modules
    "contracts",
    "benefits",
    "imports",
    "system",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {"context_processors": [
            "django.template.context_processors.debug",
            "django.template.context_processors.request",
            "django.contrib.auth.context_processors.auth",
            "django.contrib.messages.context_processors.messages",
        ]},
    }
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {"default": env.db("DATABASE_URL", default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}")}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Africa/Harare"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "accounts.User"

CORS_ALLOW_ALL_ORIGINS = env.bool("DJANGO_CORS_ALLOW_ALL", default=True)
CORS_ALLOWED_ORIGINS = env.list("DJANGO_CORS_ALLOWED_ORIGINS", default=["http://localhost:5173"])

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.URLPathVersioning",
    "DEFAULT_VERSION": "v1",
    "ALLOWED_VERSIONS": ["v1"],
    "VERSION_PARAM": "version",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "HRIS API",
    "DESCRIPTION": "HRIS API for private universities in Zimbabwe (Phase 1 modules).",
    "VERSION": "1.0.0",
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# Celery
CELERY_BROKER_URL = env("REDIS_URL", default="redis://localhost:6379/0")
CELERY_RESULT_BACKEND = env("REDIS_URL", default="redis://localhost:6379/0")
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_ALWAYS_EAGER = env.bool("CELERY_TASK_ALWAYS_EAGER", default=False)

# Celery beat schedule (runs in celery_beat container)
from celery.schedules import crontab  # noqa: E402

CELERY_BEAT_SCHEDULE = {
    "daily_notification_sweep": {
        "task": "notifications.tasks.daily_notification_sweep",
        "schedule": crontab(hour=8, minute=0),
    },
    "scheduled_backup_task": {
        "task": "system.tasks.scheduled_backup_task",
        "schedule": crontab(hour=2, minute=0),
    },
    "purge_audit_logs_task": {
        "task": "system.tasks.purge_audit_logs_task",
        "schedule": crontab(hour=3, minute=0, day_of_week="sun"),
    },
}

# HRIS configurable defaults (can be overridden via env)
DOCUMENTS_MAX_FILE_SIZE_MB = env.int("DOCUMENTS_MAX_FILE_SIZE_MB", default=10)
DOCUMENTS_ALLOWED_EXTENSIONS = env.list(
    "DOCUMENTS_ALLOWED_EXTENSIONS",
    default=["pdf", "doc", "docx", "jpg", "jpeg", "png", "img", "gif", "bmp", "webp", "tiff", "txt", "xlsx", "xls", "csv", "pptx", "ppt"],
)

ACCOUNTS_EMAIL = env("ACCOUNTS_EMAIL", default="alvinchipmunk532@gmail.com")

CONTRACT_EXPIRY_LEAD_DAYS = env.list("CONTRACT_EXPIRY_LEAD_DAYS", default=[90, 60, 30])
PROBATION_LEAD_DAYS = env.list("PROBATION_LEAD_DAYS", default=[30])
RETIREMENT_AGE = env.int("RETIREMENT_AGE", default=65)
RETIREMENT_LEAD_DAYS = env.list("RETIREMENT_LEAD_DAYS", default=[365, 180, 90])
HOLIDAY_LEAD_DAYS = env.list("HOLIDAY_LEAD_DAYS", default=[0, 1])

# Email (SMTP) - required for invite flow in production
EMAIL_HOST = env("EMAIL_HOST", default="")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)
EMAIL_USE_SSL = env.bool("EMAIL_USE_SSL", default=False)
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="no-reply@hris.local")
SERVER_EMAIL = env("SERVER_EMAIL", default=DEFAULT_FROM_EMAIL)

# SSL verification bypass for dev/testing environments with TLS inspection
# WARNING: Only use in development. Never disable in production.
EMAIL_SKIP_SSL_VERIFY = env.bool("EMAIL_SKIP_SSL_VERIFY", default=False)

# Backend logic: Use console in DEBUG if no host is configured or credentials look like placeholders
placeholder_users = {
    "email@gmail.com",
    "example@gmail.com",
    "your_email@gmail.com",
    "user@example.com",
}
placeholder_passwords = {"secret_key", "password", "changeme", ""}

is_placeholder = (
    not EMAIL_HOST
    or "yourdomain.com" in (EMAIL_HOST or "")
    or "your_smtp_username" in (EMAIL_HOST_USER or "")
    or (EMAIL_HOST_USER or "").lower() in placeholder_users
    or (EMAIL_HOST_PASSWORD or "") in placeholder_passwords
)
if DEBUG and is_placeholder:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
else:
    EMAIL_BACKEND = env(
        "DJANGO_EMAIL_BACKEND",
        default="config.email_backend.CertifiEmailBackend",
    )

# Invite links
FRONTEND_BASE_URL = env("FRONTEND_BASE_URL", default="http://localhost:5173")
INVITE_ACCEPT_PATH = env("INVITE_ACCEPT_PATH", default="/accept-invite")
INVITE_EXPIRE_DAYS = env.int("INVITE_EXPIRE_DAYS", default=7)
