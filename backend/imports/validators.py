from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Tuple

from django.utils.dateparse import parse_date

from employees.models import Employee, Department, Position, ContractType
from leaveapp.models import LeaveType, LeaveBalance
from contracts.models import Contract

from .utils import normalize_str


def _parse_date(v: Any):
    if v is None or str(v).strip() == "":
        return None
    if hasattr(v, "date"):
        try:
            return v.date().isoformat()
        except Exception:
            pass
    if isinstance(v, (datetime,)):
        return v.date().isoformat()
    
    # Try parsing string
    s = str(v).strip()
    if not s:
        return None
        
    d = parse_date(s)
    if d:
        return d.isoformat()
    return None


def validate_employees(rows: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Validate employee import rows.

    Expected fields (after mapping):
      employee_number, email, first_name, last_name, department, position, is_academic,
      grade, school, hire_date, end_date, contract_type, date_of_birth, title, gender
    """
    cleaned = []
    errors = []

    seen_empno = set()
    for idx, r in enumerate(rows, start=2):
        empno = normalize_str(r.get("employee_number"))
        email = normalize_str(r.get("email"))
        dept = normalize_str(r.get("department"))
        pos = normalize_str(r.get("position"))

        row_errors = []
        if not empno:
            row_errors.append("employee_number is required")
        if not email:
            row_errors.append("email is required")
        if not dept:
            row_errors.append("department is required")
        if not pos:
            row_errors.append("position is required")

        if empno in seen_empno:
            row_errors.append("duplicate employee_number in file")
        else:
            seen_empno.add(empno)

        if empno and Employee.objects.filter(employee_number=empno).exists():
            row_errors.append("employee_number already exists")

        if email:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            existing_user = User.objects.filter(email=email).first()
            if existing_user:
                try:
                    # If user exists, check if they already have an employee profile
                    # Try to access safely in case migrations aren't run
                    existing_emp = getattr(existing_user, "employee_profile", None)
                    if existing_emp:
                        # Only error if it's a DIFFERENT employee number
                        if existing_emp.employee_number != empno:
                            row_errors.append(f"email {email} is already assigned to another employee ({existing_emp.employee_number})")
                except Exception:
                    # Likely a DB column missing error
                    pass

        if row_errors:
            errors.append({"row": idx, "employee_number": empno, "errors": row_errors})
            continue

        cleaned.append({
            "employee_number": empno,
            "email": email,
            "first_name": normalize_str(r.get("first_name")),
            "last_name": normalize_str(r.get("last_name")),
            "department": dept,
            "position": pos,
            "is_academic": str(r.get("is_academic") or "").strip().lower() in ("1", "true", "yes", "y"),
            "employment_status": normalize_str(r.get("employment_status")) or "ACTIVE",
            "contract_type": (normalize_str(r.get("contract_type")) or "PERMANENT").upper().replace(" ", "_"),
            "hire_date": _parse_date(r.get("hire_date") or r.get("start_date")),
            "end_date": _parse_date(r.get("end_date") or r.get("end-date")),
            "line_manager_email": normalize_str(r.get("line_manager_email")),
            "date_of_birth": _parse_date(r.get("date_of_birth")),
            "national_id": normalize_str(r.get("national_id") or r.get("national_id/passport_number")),
            "title": (normalize_str(r.get("title")) or "").upper(),
            "gender": (normalize_str(r.get("gender")) or "").upper(),
            "grade": normalize_str(r.get("grade")),
            "school": normalize_str(r.get("school")),
        })

    return cleaned, errors


def commit_employees(cleaned: List[Dict[str, Any]], creator=None):
    from django.contrib.auth import get_user_model
    from accounts.utils import create_and_send_invite
    User = get_user_model()

    created = 0
    for r in cleaned:
        dept, _ = Department.objects.get_or_create(name=r["department"], defaults={"code": ""})
        pos, _ = Position.objects.get_or_create(title=r["position"], department=dept, defaults={"is_academic": r["is_academic"]})

        user = User.objects.filter(email=r["email"]).first()
        if user:
            # Update existing user info
            user.first_name = r.get("first_name") or user.first_name
            user.last_name = r.get("last_name") or user.last_name
            user.save(update_fields=["first_name", "last_name"])
        else:
            user = User.objects.create_user(
                email=r["email"],
                password=None,
                first_name=r.get("first_name") or "",
                last_name=r.get("last_name") or "",
                role=User.Role.EMPLOYEE,
            )

        lm_user = None
        if r.get("line_manager_email"):
            lm_user = User.objects.filter(email=r["line_manager_email"]).first()

        Employee.objects.create(
            user=user,
            employee_number=r["employee_number"],
            department=dept,
            position=pos,
            employment_status=r.get("employment_status") or "ACTIVE",
            contract_type=r.get("contract_type") or "PERMANENT",
            hire_date=r.get("hire_date"),
            end_date=r.get("end_date"),
            line_manager=lm_user,
            date_of_birth=r.get("date_of_birth"),
            national_id=r.get("national_id"),
            title=r.get("title") or None,
            gender=r.get("gender") or None,
            grade=r.get("grade"),
            school=r.get("school"),
        )
        
        # Send invite link if the user doesn't have a usable password
        if not user.has_usable_password():
            create_and_send_invite(user, creator)
            
        created += 1
    return {"created": created}


def validate_leave_balances(rows: List[Dict[str, Any]]):
    cleaned = []
    errors = []
    for idx, r in enumerate(rows, start=2):
        empno = normalize_str(r.get("employee_number"))
        leave_type_name = normalize_str(r.get("leave_type"))
        year = normalize_str(r.get("year"))
        days_entitled = r.get("days_entitled")
        days_used = r.get("days_used")

        row_errors = []
        if not empno:
            row_errors.append("employee_number is required")
        if not leave_type_name:
            row_errors.append("leave_type is required")
        try:
            year_i = int(year)
        except Exception:
            row_errors.append("year must be an integer")
            year_i = None

        emp = Employee.objects.filter(employee_number=empno).first() if empno else None
        if empno and not emp:
            row_errors.append("employee_number not found")

        lt = LeaveType.objects.filter(name__iexact=leave_type_name).first() if leave_type_name else None
        if leave_type_name and not lt:
            row_errors.append("leave_type not found")

        try:
            de = int(days_entitled) if days_entitled is not None and str(days_entitled).strip() != "" else 0
        except Exception:
            row_errors.append("days_entitled must be an integer")
            de = 0
        try:
            du = int(days_used) if days_used is not None and str(days_used).strip() != "" else 0
        except Exception:
            row_errors.append("days_used must be an integer")
            du = 0

        if row_errors:
            errors.append({"row": idx, "employee_number": empno, "errors": row_errors})
            continue

        cleaned.append({"employee": emp, "leave_type": lt, "year": year_i, "days_entitled": de, "days_used": du})

    return cleaned, errors


def commit_leave_balances(cleaned):
    updated = 0
    created = 0
    for r in cleaned:
        obj, is_created = LeaveBalance.objects.update_or_create(
            employee=r["employee"],
            leave_type=r["leave_type"],
            year=r["year"],
            defaults={"days_entitled": r["days_entitled"], "days_used": r["days_used"]},
        )
        if is_created:
            created += 1
        else:
            updated += 1
    return {"created": created, "updated": updated}


def validate_contracts(rows: List[Dict[str, Any]]):
    cleaned = []
    errors = []
    for idx, r in enumerate(rows, start=2):
        empno = normalize_str(r.get("employee_number"))
        start_date = _parse_date(r.get("start_date"))
        end_date = _parse_date(r.get("end_date"))
        probation_end_date = _parse_date(r.get("probation_end_date"))
        contract_type = (normalize_str(r.get("contract_type")) or "PERMANENT").upper().replace(" ", "_")

        row_errors = []
        emp = Employee.objects.filter(employee_number=empno).first() if empno else None
        if not empno:
            row_errors.append("employee_number is required")
        if empno and not emp:
            row_errors.append("employee_number not found")
        if not start_date:
            row_errors.append("start_date is required")

        if row_errors:
            errors.append({"row": idx, "employee_number": empno, "errors": row_errors})
            continue

        cleaned.append({
            "employee": emp,
            "start_date": start_date,
            "end_date": end_date,
            "probation_end_date": probation_end_date,
            "contract_type": contract_type,
        })

    return cleaned, errors


def commit_contracts(cleaned):
    created = 0
    for r in cleaned:
        Contract.objects.create(**r)
        created += 1
    return {"created": created}
