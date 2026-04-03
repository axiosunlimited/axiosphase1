from typing import List

from .models import ApprovalProcessConfig


def allowed_roles_for(process_code: str, default_roles: List[str]) -> List[str]:
    """Return allowed roles for a process code.

    If a config exists and is_active, its allowed_roles is used.
    Otherwise, `default_roles` is returned.
    """
    try:
        cfg = ApprovalProcessConfig.objects.filter(process_code=process_code, is_active=True).first()
        if cfg and isinstance(cfg.allowed_roles, list) and cfg.allowed_roles:
            return cfg.allowed_roles
    except Exception:
        pass
    return default_roles
