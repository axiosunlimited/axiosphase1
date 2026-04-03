from __future__ import annotations

from datetime import timedelta, date

from celery import shared_task
from django.utils import timezone
from django.conf import settings

from accounts.models import User
from employees.models import Employee

from .utils import notify_user
from system.utils import get_setting_int, get_setting_list
from django.core.mail import send_mail

@shared_task
def send_async_email(subject, message, from_email, recipient_list, fail_silently=False):
    """
    Sends an email asynchronously to avoid blocking the request worker.
    """
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list,
            fail_silently=fail_silently
        )
        return True
    except Exception as e:
        if not fail_silently:
            raise e
        return False

def _get_int_list(val, default):
    if isinstance(val, list):
        out = []
        for x in val:
            try:
                out.append(int(x))
            except Exception:
                pass
        return out or default
    return default



@shared_task
def daily_notification_sweep():
    today = timezone.now().date()

    # Birthdays
    bdays = Employee.objects.select_related("user").filter(date_of_birth__month=today.month, date_of_birth__day=today.day)
    for emp in bdays:
        notify_user(emp.user, key="birthday", context={"message": "Happy birthday!"}, title="Birthday")

    # Public holiday notices (tomorrow)
    try:
        from leaveapp.models import PublicHoliday
        # Configurable via SystemSetting key: notification.public_holiday_lead_days
        lead_days = _get_int_list(get_setting_list("notification.public_holiday_lead_days", getattr(settings, "HOLIDAY_LEAD_DAYS", [0, 1])), [0, 1])
        for days in lead_days:
            target = today + timedelta(days=days)
            hols = PublicHoliday.objects.filter(date=target)
            for h in hols:
                title = "Public Holiday"
                prefix = "Today" if days == 0 else f"In {days} day(s)"
                msg = f"{prefix}: {h.name} ({target.isoformat()})."
                for u in User.objects.filter(is_active=True):
                    notify_user(u, key="public_holiday", context={"message": msg, "days": days}, title=title)
    except Exception:
        pass

    # Contract expiries / probation / retirement
    try:
        from contracts.models import Contract
    except Exception:
        Contract = None

    if Contract is not None:
        # configurable lead times (days)
        lead_times = _get_int_list(
            get_setting_list("notification.contract_expiry_lead_days", getattr(settings, "CONTRACT_EXPIRY_LEAD_DAYS", [90, 60, 30])),
            [90, 60, 30],
        )
        for days in lead_times:
            target = today + timedelta(days=days)
            qs = Contract.objects.select_related("employee", "employee__user").filter(end_date=target)
            for c in qs:
                emp = c.employee
                msg = f"Contract for {emp.employee_number} expires on {c.end_date.isoformat()} ({days} days)."
                notify_user(emp.user, key="contract_expiry", context={"message": msg, "days": days})
                if emp.line_manager:
                    notify_user(emp.line_manager, key="contract_expiry_team", context={"message": msg, "employee": emp.employee_number, "days": days})

        # probation end alerts
        prob_days = _get_int_list(
            get_setting_list("notification.probation_lead_days", getattr(settings, "PROBATION_LEAD_DAYS", [30])),
            [30],
        )
        for days in prob_days:
            target = today + timedelta(days=days)
            qs = Contract.objects.select_related("employee", "employee__user").filter(probation_end_date=target)
            for c in qs:
                emp = c.employee
                msg = f"Probation period for {emp.employee_number} ends on {c.probation_end_date.isoformat()} ({days} days)."
                notify_user(emp.user, key="probation_end", context={"message": msg, "days": days})
                if emp.line_manager:
                    notify_user(emp.line_manager, key="probation_end_team", context={"message": msg, "employee": emp.employee_number, "days": days})

    # Retirement approaching (based on date_of_birth)
    retirement_age = int(get_setting_int("notification.retirement_age", int(getattr(settings, "RETIREMENT_AGE", 65))))
    lead_times = _get_int_list(
        get_setting_list("notification.retirement_lead_days", getattr(settings, "RETIREMENT_LEAD_DAYS", [365, 180, 90])),
        [365, 180, 90],
    )

    for emp in Employee.objects.select_related("user").exclude(date_of_birth__isnull=True):
        dob = emp.date_of_birth
        if not dob:
            continue
        try:
            retirement_date = date(dob.year + retirement_age, dob.month, dob.day)
        except ValueError:
            retirement_date = date(dob.year + retirement_age, dob.month, dob.day - 1)
        for days in lead_times:
            if retirement_date == today + timedelta(days=days):
                msg = f"Retirement for {emp.employee_number} is on {retirement_date.isoformat()} ({days} days)."
                notify_user(emp.user, key="retirement", context={"message": msg, "days": days})
                if emp.line_manager:
                    notify_user(emp.line_manager, key="retirement_team", context={"message": msg, "employee": emp.employee_number, "days": days})

    return {"date": today.isoformat()}
