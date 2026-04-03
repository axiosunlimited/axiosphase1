from __future__ import annotations

import gzip
import json
from io import BytesIO
from datetime import timedelta

from django.core.management import call_command
from django.utils import timezone
from django.core.files.base import ContentFile

from .models import BackupArtifact, SystemSetting


def _retention_days_default() -> int:
    return 365


def purge_audit_logs_queryset(qs):
    # helper in case we want to call without importing audit in migrations
    qs.delete()


def create_backup(created_by=None) -> BackupArtifact:
    """Create a JSON backup using Django dumpdata (compressed).

    This is not a full physical pg_dump, but satisfies the *application-level* backup
    requirement in the doc. For production, prefer DB-level backups.
    """

    out = BytesIO()
    call_command(
        "dumpdata",
        "--natural-foreign",
        "--natural-primary",
        "--indent",
        "2",
        stdout=out,
    )
    out.seek(0)

    gz = BytesIO()
    with gzip.GzipFile(fileobj=gz, mode="wb") as f:
        f.write(out.read())
    gz.seek(0)

    filename = f"backup_{timezone.now().strftime('%Y%m%d_%H%M%S')}.json.gz"
    obj = BackupArtifact(created_by=created_by)
    obj.file.save(filename, ContentFile(gz.read()), save=False)
    obj.size_bytes = obj.file.size or 0
    obj.save()
    return obj


def get_setting_int(key: str, default: int) -> int:
    val = SystemSetting.get_value(key, default)
    try:
        if isinstance(val, dict) and "value" in val:
            val = val["value"]
        return int(val)
    except Exception:
        return default


def get_setting_list(key: str, default: list[str]) -> list[str]:
    val = SystemSetting.get_value(key, default)
    if isinstance(val, list):
        return [str(x) for x in val]
    if isinstance(val, dict) and isinstance(val.get("value"), list):
        return [str(x) for x in val.get("value")]
    return default
