from __future__ import annotations

from datetime import date, timedelta
from typing import Any, Dict

from django.db.models import Count, Sum
from django.utils import timezone

from employees.models import Employee, Department, Position
from recruitment.models import Vacancy, Applicant, Appointment
from leaveapp.models import LeaveRequest
from performance.models import Appraisal

try:
    from training.models import EmployeeTraining
except Exception:
    EmployeeTraining = None

try:
    from workforce.models import EstablishmentItem, Separation
except Exception:
    EstablishmentItem = None
    Separation = None


PREDEFINED_REPORTS = {
    "council_summary": {
        "name": "Council Summary",
        "audience": "Council",
        "description": "High-level headcount, vacancies, leave, performance, training and workforce indicators.",
    },
    "hr_committee": {
        "name": "HR Committee Report",
        "audience": "HR Committee",
        "description": "Operational HR metrics: recruitment pipeline, leave workload, performance progress and staffing changes.",
    },
    "workforce_planning": {
        "name": "Workforce Planning",
        "audience": "HR/Management",
        "description": "Staff establishment vs actual headcount, academic vs non-academic ratios, vacancies and separations.",
    },
    "hr_alerts": {
        "name": "HR Alerts Dashboard",
        "audience": "HR/Admin",
        "description": "Contracts expiring, probation endings, retirements, missing documents, and leave trends.",
    },
    "education_assistance": {
        "name": "Education Assistance Report",
        "audience": "HR/Finance",
        "description": "Claims and costs by department/level, pending approvals, and yearly totals.",
    },
}


def _year_from_request(params: Dict[str, Any]) -> int:
    y = params.get("year")
    if y:
        try:
            return int(y)
        except Exception:
            pass
    return timezone.now().year


def run_predefined(key: str, params: Dict[str, Any]) -> Dict[str, Any]:
    if key not in PREDEFINED_REPORTS:
        raise ValueError("Unknown predefined report")

    year = _year_from_request(params)

    if key == "council_summary":
        total = Employee.objects.count()
        academic = Employee.objects.filter(position__is_academic=True).count()
        non_academic = Employee.objects.filter(position__is_academic=False).count()

        headcount_by_dept = list(
            Department.objects.annotate(headcount=Count("employees")).values("name", "headcount").order_by("name")
        )

        vacancies_by_status = list(
            Vacancy.objects.values("status").annotate(count=Count("id")).order_by("status")
        )

        leave_counts = list(
            LeaveRequest.objects.filter(start_date__year=year).values("status").annotate(count=Count("id")).order_by("status")
        )

        appraisal_counts = list(
            Appraisal.objects.filter(year=year).values("status").annotate(count=Count("id")).order_by("status")
        )

        training_spend = None
        if EmployeeTraining is not None:
            training_spend = EmployeeTraining.objects.filter(recorded_at__year=year).aggregate(total=Sum("cost")).get("total") or 0

        separations_count = None
        if Separation is not None:
            separations_count = Separation.objects.filter(separation_date__year=year).count()

        return {
            "report": PREDEFINED_REPORTS[key],
            "params": {"year": year},
            "generated_at": timezone.now().isoformat(),
            "metrics": {
                "total_employees": total,
                "academic_employees": academic,
                "non_academic_employees": non_academic,
                "headcount_by_department": headcount_by_dept,
                "vacancies_by_status": vacancies_by_status,
                "leave_requests_by_status": leave_counts,
                "appraisals_by_status": appraisal_counts,
                "training_spend_total": float(training_spend) if training_spend is not None else None,
                "separations_count": separations_count,
            },
        }

    if key == "hr_committee":
        vacancies_open = Vacancy.objects.filter(status__in=[Vacancy.Status.SUBMITTED, Vacancy.Status.APPROVED, Vacancy.Status.PUBLISHED]).count()
        applicants_total = Applicant.objects.count()
        appointments_total = Appointment.objects.count()

        pipeline_by_vacancy = list(
            Vacancy.objects.annotate(applicant_count=Count("applicants")).values("id", "title", "status", "applicant_count").order_by("-created_at")[:50]
        )

        leave_qs = LeaveRequest.objects.filter(start_date__year=year)
        pending_by_stage = {
            "pending_line_manager": leave_qs.filter(status=LeaveRequest.Status.PENDING_LM).count(),
            "pending_hr": leave_qs.filter(status=LeaveRequest.Status.PENDING_HR).count(),
            "pending_pvc": leave_qs.filter(status=LeaveRequest.Status.PENDING_PVC).count(),
            "pending_admin": leave_qs.filter(status=LeaveRequest.Status.PENDING_ADMIN).count(),
            "pending_finance": leave_qs.filter(status=LeaveRequest.Status.PENDING_FINANCE).count(),
        }
        leave_pending = sum(pending_by_stage.values())
        leave_approved = leave_qs.filter(status=LeaveRequest.Status.APPROVED).count()
        leave_rejected = leave_qs.filter(status=LeaveRequest.Status.REJECTED).count()

        appraisal_in_progress = Appraisal.objects.filter(year=year).exclude(status=Appraisal.Status.FINALIZED).count()

        training_count = None
        if EmployeeTraining is not None:
            training_count = EmployeeTraining.objects.filter(recorded_at__year=year).count()

        return {
            "report": PREDEFINED_REPORTS[key],
            "params": {"year": year},
            "generated_at": timezone.now().isoformat(),
            "metrics": {
                "vacancies_open_workflow": vacancies_open,
                "applicants_total": applicants_total,
                "appointments_total": appointments_total,
                "recruitment_pipeline": pipeline_by_vacancy,
                "leave_pending_total": leave_pending,
                "leave_pending_by_stage": pending_by_stage,
                "leave_approved": leave_approved,
                "leave_rejected": leave_rejected,
                "appraisals_in_progress": appraisal_in_progress,
                "training_records_count": training_count,
            },
        }

    if key == "workforce_planning":
        headcount_total = Employee.objects.count()
        academic = Employee.objects.filter(position__is_academic=True).count()
        non_academic = Employee.objects.filter(position__is_academic=False).count()

        est_rows = []
        if EstablishmentItem is not None:
            # Establishment vs actual headcount for the year
            est_items = EstablishmentItem.objects.filter(year=year).select_related("department", "position")
            for item in est_items:
                actual = Employee.objects.filter(department=item.department, position=item.position).count()
                est_rows.append({
                    "year": item.year,
                    "department": item.department.name,
                    "position": item.position.title,
                    "budgeted_headcount": item.budgeted_headcount,
                    "actual_headcount": actual,
                    "vacancy_gap": max(0, item.budgeted_headcount - actual),
                })

        separations = None
        if Separation is not None:
            separations = list(
                Separation.objects.filter(separation_date__year=year).values("separation_type").annotate(count=Count("id")).order_by("separation_type")
            )

        vacancies_published = Vacancy.objects.filter(status=Vacancy.Status.PUBLISHED).count()

        return {
            "report": PREDEFINED_REPORTS[key],
            "params": {"year": year},
            "generated_at": timezone.now().isoformat(),
            "metrics": {
                "headcount_total": headcount_total,
                "academic_ratio": (academic / headcount_total) if headcount_total else None,
                "non_academic_ratio": (non_academic / headcount_total) if headcount_total else None,
                "establishment_vs_actual": est_rows,
                "separations_by_type": separations,
                "vacancies_published": vacancies_published,
            },
        }

    if key == "hr_alerts":
        today = timezone.now().date()
        days = int(params.get("days") or 90)
        retirement_days = int(params.get("retirement_days") or 365)

        contracts_expiring = []
        probation_ending = []
        retirements = []

        try:
            from contracts.models import Contract

            exp_qs = Contract.objects.select_related("employee", "employee__user").filter(
                end_date__isnull=False,
                end_date__gte=today,
                end_date__lte=today + timedelta(days=days),
            )
            for c in exp_qs[:200]:
                contracts_expiring.append({
                    "employee_number": c.employee.employee_number,
                    "name": c.employee.user.full_name,
                    "end_date": c.end_date.isoformat() if c.end_date else None,
                })

            prob_qs = Contract.objects.select_related("employee", "employee__user").filter(
                probation_end_date__isnull=False,
                probation_end_date__gte=today,
                probation_end_date__lte=today + timedelta(days=days),
            )
            for c in prob_qs[:200]:
                probation_ending.append({
                    "employee_number": c.employee.employee_number,
                    "name": c.employee.user.full_name,
                    "probation_end_date": c.probation_end_date.isoformat() if c.probation_end_date else None,
                })
        except Exception:
            pass

        retirement_age = int(params.get("retirement_age") or 65)
        for e in Employee.objects.select_related("user").exclude(date_of_birth__isnull=True):
            dob = e.date_of_birth
            if not dob:
                continue
            try:
                rdate = date(dob.year + retirement_age, dob.month, dob.day)
            except Exception:
                continue
            if today <= rdate <= (today + timedelta(days=retirement_days)):
                retirements.append({
                    "employee_number": e.employee_number,
                    "name": e.user.full_name,
                    "retirement_date": rdate.isoformat(),
                })

        # Missing required documents
        required_categories = [
            "NATIONAL_ID_OR_PASSPORT",
            "ACADEMIC_CERTIFICATES",
            "PROFESSIONAL_CERTIFICATIONS",
            "CV",
            "BANKING_DETAILS",
        ]
        try:
            from employees.models import EmployeeDocument

            missing = []
            for e in Employee.objects.select_related("user")[:500]:
                existing = set(
                    EmployeeDocument.objects.filter(employee=e, is_latest=True).values_list("category", flat=True)
                )
                miss = [c for c in required_categories if c not in existing]
                if miss:
                    missing.append({
                        "employee_number": e.employee_number,
                        "name": e.user.full_name,
                        "missing_categories": miss,
                    })
        except Exception:
            missing = []

        # Leave trend overview (last 12 months)
        trend = []
        try:
            from django.db.models.functions import TruncMonth

            start = (today.replace(day=1) - timedelta(days=365))
            qs = LeaveRequest.objects.filter(start_date__gte=start).annotate(m=TruncMonth("start_date")).values("m").annotate(count=Count("id")).order_by("m")
            for r in qs:
                m = r["m"]
                trend.append({"month": m.date().isoformat() if m else None, "count": r["count"]})
        except Exception:
            pass

        return {
            "report": PREDEFINED_REPORTS[key],
            "params": {"days": days, "retirement_days": retirement_days, "retirement_age": retirement_age},
            "generated_at": timezone.now().isoformat(),
            "metrics": {
                "contracts_expiring": contracts_expiring,
                "probation_ending": probation_ending,
                "retirements": retirements,
                "missing_documents": missing,
                "leave_trend": trend,
            },
        }

    if key == "education_assistance":
        year = _year_from_request(params)
        try:
            from benefits.models import EducationClaim, Dependant
        except Exception:
            raise ValueError("Education Assistance module not installed")

        claims = EducationClaim.objects.select_related("employee", "employee__department", "dependant").filter(academic_year=year)
        total_claimed = claims.aggregate(total=Sum("amount_claimed")).get("total") or 0
        total_approved = claims.aggregate(total=Sum("amount_approved")).get("total") or 0

        by_dept = list(
            claims.values("employee__department__name").annotate(total=Sum("amount_approved")).order_by("employee__department__name")
        )
        by_level = list(
            claims.values("dependant__education_level").annotate(total=Sum("amount_approved")).order_by("dependant__education_level")
        )
        status_counts = list(claims.values("status").annotate(count=Count("id")).order_by("status"))

        return {
            "report": PREDEFINED_REPORTS[key],
            "params": {"year": year},
            "generated_at": timezone.now().isoformat(),
            "metrics": {
                "total_claimed": float(total_claimed),
                "total_approved": float(total_approved) if total_approved is not None else None,
                "by_department": by_dept,
                "by_education_level": by_level,
                "status_counts": status_counts,
            },
        }

    raise ValueError("Unhandled predefined report")
