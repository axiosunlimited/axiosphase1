"""
Role-based analytics dashboards for HRIS.
Returns aggregated metrics specific to user role.
"""
from datetime import date, timedelta
from typing import Dict, Any

from django.db.models import Count, Q, F, Sum, Avg, Case, When, IntegerField
from django.utils import timezone

from accounts.models import User
from employees.models import Employee, Department
from leaveapp.models import LeaveRequest, LeaveBalance
from contracts.models import Contract
from benefits.models import EducationClaim, DependantDocument
from recruitment.models import Vacancy, Applicant
from notifications.models import SystemAlert


def get_system_admin_dashboard(params: Dict[str, Any]) -> Dict[str, Any]:
    """Full system overview for System Admin."""
    today = timezone.now().date()
    year = params.get("year") or today.year
    try:
        year = int(year)
    except (ValueError, TypeError):
        year = today.year
    
    total_employees = Employee.objects.count()
    active_employees = Employee.objects.filter(employment_status="ACTIVE").count()
    
    # Employee by department
    employees_by_dept = list(
        Department.objects.annotate(count=Count("employees")).values("name", "count")
        .order_by("-count")[:10]
    )

    # Contracts expiring soon (next 90 days)
    contract_threshold = today + timedelta(days=90)
    contracts_expiring = Contract.objects.filter(
        end_date__lte=contract_threshold,
        end_date__gte=today,
        employee__employment_status="ACTIVE"
    ).count()

    # Leave requests this year
    leave_by_status = list(
        LeaveRequest.objects.filter(start_date__year=year).values("status")
        .annotate(count=Count("id")).order_by("status")
    )

    # Active vacancies
    active_vacancies = Vacancy.objects.filter(status="OPEN").count()
    pending_applicants = Applicant.objects.filter(status="PENDING").count()

    # System alerts
    active_alerts = SystemAlert.objects.filter(status="ACTIVE").count()

    # Users by role
    users_by_role = list(
        User.objects.exclude(role="EMPLOYEE").values("role")
        .annotate(count=Count("id")).order_by("role")
    )

    return {
        "dashboard_type": "system_admin",
        "metrics": {
            "total_employees": total_employees,
            "active_employees": active_employees,
            "contracts_expiring_soon": contracts_expiring,
            "active_vacancies": active_vacancies,
            "pending_applicants": pending_applicants,
            "active_system_alerts": active_alerts,
        },
        "charts": {
            "employees_by_department": employees_by_dept,
            "leave_by_status": leave_by_status,
            "users_by_role": users_by_role,
        },
    }


def get_hr_manager_dashboard(params: Dict[str, Any]) -> Dict[str, Any]:
    """HR Manager dashboard with recruitment, leave, and contract overview."""
    today = timezone.now().date()
    year = params.get("year") or today.year
    try:
        year = int(year)
    except (ValueError, TypeError):
        year = today.year

    total_employees = Employee.objects.count()
    active_employees = Employee.objects.filter(employment_status="ACTIVE").count()

    # Recruitment pipeline
    open_vacancies = Vacancy.objects.filter(status="OPEN").count()
    interviews_pending = list(
        Applicant.objects.filter(status="INTERVIEW_PENDING").values("vacancy__title")
        .annotate(count=Count("id")).order_by("-count")[:5]
    )

    # Leave summary this year
    leave_pending = LeaveRequest.objects.filter(status__in=["PENDING_LM", "PENDING_HR"], start_date__year=year).count()
    leave_approved = LeaveRequest.objects.filter(status="APPROVED", start_date__year=year).count()
    leave_rejected = LeaveRequest.objects.filter(status="REJECTED", start_date__year=year).count()

    # Contracts expiring
    contract_threshold = today + timedelta(days=90)
    contracts_expiring = Contract.objects.filter(
        end_date__lte=contract_threshold,
        end_date__gte=today,
        employee__employment_status="ACTIVE"
    ).count()

    # Probation ending soon
    probation_threshold = today + timedelta(days=30)
    probation_ending = Contract.objects.filter(
        probation_end_date__lte=probation_threshold,
        probation_end_date__gte=today,
        employee__employment_status="ACTIVE"
    ).count()

    # Employees nearing retirement
    retirement_year = today.year
    nearing_retirement = Employee.objects.filter(
        retirement_date__year=retirement_year,
        retirement_date__gte=today,
        employment_status="ACTIVE"
    ).count()

    # Missing documents (no ID/passport uploaded)
    missing_docs = Employee.objects.annotate(
        has_docs=Count("documents")
    ).filter(has_docs=0).count()

    # Education claims pending approval
    claims_pending_hr = EducationClaim.objects.filter(status="SUBMITTED").count()

    # Leave trends by type (top 5)
    leave_by_type = list(
        LeaveRequest.objects.filter(start_date__year=year).values("leave_type__name")
        .annotate(count=Count("id")).order_by("-count")[:5]
    )

    return {
        "dashboard_type": "hr_manager",
        "metrics": {
            "total_employees": total_employees,
            "active_employees": active_employees,
            "open_vacancies": open_vacancies,
            "leave_pending_approval": leave_pending,
            "contracts_expiring_soon": contracts_expiring,
            "probation_ending_soon": probation_ending,
            "retiring_this_year": nearing_retirement,
            "missing_required_documents": missing_docs,
            "education_claims_pending": claims_pending_hr,
        },
        "charts": {
            "interviews_pending_by_vacancy": interviews_pending,
            "leave_summary": [
                {"status": "Pending", "count": leave_pending},
                {"status": "Approved", "count": leave_approved},
                {"status": "Rejected", "count": leave_rejected},
            ],
            "leave_by_type": leave_by_type,
        },
    }


def get_line_manager_dashboard(user: User, params: Dict[str, Any]) -> Dict[str, Any]:
    """Line Manager dashboard - team-specific metrics."""
    today = timezone.now().date()
    year = params.get("year") or today.year
    try:
        year = int(year)
    except (ValueError, TypeError):
        year = today.year

    # Get direct reports
    team = Employee.objects.filter(line_manager=user)
    team_count = team.count()
    
    # On leave today or near future
    on_leave_count = LeaveRequest.objects.filter(
        employee__line_manager=user,
        status="APPROVED",
        start_date__lte=today,
        end_date__gte=today
    ).count()

    # Pending leave requests
    pending_requests = LeaveRequest.objects.filter(
        employee__line_manager=user,
        status="PENDING_LM"
    ).count()

    # Team leave by type (this year)
    team_leave_by_type = list(
        LeaveRequest.objects.filter(
            employee__line_manager=user,
            start_date__year=year
        ).values("leave_type__name").annotate(count=Count("id")).order_by("-count")[:5]
    )

    # Team leave balances (current year)
    team_leave_balances = list(
        LeaveBalance.objects.filter(
            employee__line_manager=user,
            year=year
        ).values("leave_type__name").annotate(
            total_entitled=Sum("days_entitled"),
            total_used=Sum("days_used")
        ).order_by("leave_type__name")
    )

    # Team contracts expiring
    contract_threshold = today + timedelta(days=90)
    team_contracts_expiring = Contract.objects.filter(
        employee__line_manager=user,
        end_date__lte=contract_threshold,
        end_date__gte=today,
        employee__employment_status="ACTIVE"
    ).count()

    # Team members by department
    team_by_dept = list(
        team.values("department__name").annotate(count=Count("id"))
        .order_by("department__name")
    )

    return {
        "dashboard_type": "line_manager",
        "metrics": {
            "team_size": team_count,
            "on_leave_today": on_leave_count,
            "pending_leave_requests": pending_requests,
            "team_contracts_expiring": team_contracts_expiring,
        },
        "charts": {
            "team_leave_by_type": team_leave_by_type,
            "team_leave_balances": team_leave_balances,
            "team_by_department": team_by_dept,
        },
    }


def get_finance_officer_dashboard(params: Dict[str, Any]) -> Dict[str, Any]:
    """Finance Officer dashboard - benefits and claims overview."""
    today = timezone.now().date()
    year = params.get("year") or today.year
    try:
        year = int(year)
    except (ValueError, TypeError):
        year = today.year

    # Education claims
    claims_total = EducationClaim.objects.count()
    claims_paid = EducationClaim.objects.filter(status="PAID").count()
    claims_pending_finance = EducationClaim.objects.filter(status="FINANCE_PENDING").count()
    claims_needs_info = EducationClaim.objects.filter(status="NEEDS_INFO").count()

    # Total claimed this year
    claims_this_year = EducationClaim.objects.filter(academic_year=year)
    total_claimed = claims_this_year.aggregate(total=Sum("amount_claimed"))["total"] or 0
    total_paid = claims_this_year.filter(status="PAID").aggregate(total=Sum("amount_approved"))["total"] or 0
    total_pending = claims_this_year.exclude(status="PAID").aggregate(total=Sum("amount_claimed"))["total"] or 0

    # Claims by status
    claims_by_status = list(
        EducationClaim.objects.filter(academic_year=year).values("status")
        .annotate(count=Count("id"), total=Sum("amount_claimed")).order_by("status")
    )

    # Top claiming employees
    top_claimants = list(
        EducationClaim.objects.filter(academic_year=year).values(
            "employee__user__first_name",
            "employee__user__last_name",
            "employee__employee_number"
        ).annotate(
            claim_count=Count("id"),
            total_claimed=Sum("amount_claimed")
        ).order_by("-total_claimed")[:5]
    )

    # Claims by department
    claims_by_dept = list(
        EducationClaim.objects.filter(academic_year=year).values("employee__department__name")
        .annotate(count=Count("id"), total=Sum("amount_claimed")).order_by("-total")[:8]
    )

    return {
        "dashboard_type": "finance_officer",
        "metrics": {
            "total_claims": claims_total,
            "claims_paid": claims_paid,
            "claims_pending_finance": claims_pending_finance,
            "claims_needing_info": claims_needs_info,
            "total_amount_claimed_this_year": float(total_claimed),
            "total_amount_paid_this_year": float(total_paid),
            "total_amount_pending_this_year": float(total_pending),
        },
        "charts": {
            "claims_by_status": claims_by_status,
            "top_claimants": top_claimants,
            "claims_by_department": claims_by_dept,
        },
    }


def get_employee_dashboard(user: User, params: Dict[str, Any]) -> Dict[str, Any]:
    """Employee self-service dashboard."""
    today = timezone.now().date()
    year = params.get("year") or today.year
    try:
        year = int(year)
    except (ValueError, TypeError):
        year = today.year

    try:
        employee = user.employee_profile
    except Employee.DoesNotExist:
        return {
            "dashboard_type": "employee",
            "metrics": {},
            "charts": {},
            "error": "Employee profile not found",
        }

    # Leave balances
    leave_balances = list(
        LeaveBalance.objects.filter(employee=employee, year=year).values(
            "leave_type__name", "days_entitled", "days_used"
        ).annotate(days_remaining=F("days_entitled") - F("days_used"))
    )

    # Recent leave requests
    recent_leaves = list(
        LeaveRequest.objects.filter(employee=employee, start_date__year=year)
        .values("start_date", "end_date", "status", "leave_type__name")
        .order_by("-start_date")[:5]
    )

    # Upcoming approved leaves
    upcoming_leaves = list(
        LeaveRequest.objects.filter(
            employee=employee,
            status="APPROVED",
            start_date__gte=today
        ).values("start_date", "end_date", "leave_type__name")
        .order_by("start_date")[:5]
    )

    # Education claims
    my_claims = list(
        EducationClaim.objects.filter(employee=employee).values(
            "academic_year", "period_label", "amount_claimed", "status"
        ).order_by("-created_at")[:5]
    )

    # Contract info
    try:
        contract = Contract.objects.filter(employee=employee).latest("start_date")
        contract_expiry = contract.end_date
    except Contract.DoesNotExist:
        contract_expiry = None

    return {
        "dashboard_type": "employee",
        "metrics": {
            "total_leave_balances": len(leave_balances),
        },
        "charts": {
            "leave_balances": leave_balances,
            "recent_leave_requests": recent_leaves,
            "upcoming_approved_leaves": upcoming_leaves,
            "my_education_claims": my_claims,
            "contract_expiry_date": str(contract_expiry) if contract_expiry else None,
        },
    }


def get_analytics_dashboard(user: User, params: Dict[str, Any]) -> Dict[str, Any]:
    """Get role-appropriate analytics dashboard."""
    # Flatten params: if values are lists, take first element
    flat_params = {}
    for k, v in params.items():
        if isinstance(v, list):
            flat_params[k] = v[0] if v else None
        else:
            flat_params[k] = v
    
    if user.role == User.Role.SYSTEM_ADMIN:
        return get_system_admin_dashboard(flat_params)
    elif user.role in [User.Role.HR_MANAGER, User.Role.HR_OFFICER]:
        return get_hr_manager_dashboard(flat_params)
    elif user.role == User.Role.LINE_MANAGER:
        return get_line_manager_dashboard(user, flat_params)
    elif user.role == User.Role.FINANCE_OFFICER:
        return get_finance_officer_dashboard(flat_params)
    else:
        # Employee or other roles
        return get_employee_dashboard(user, flat_params)
