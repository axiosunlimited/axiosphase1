"""
Dashboard API — returns role-aware stats, alerts, and summaries.

HR/Admin roles get the full alerts dashboard.
Employees get their own leave balances, claims, notifications, and profile.
"""
from __future__ import annotations

from datetime import date, timedelta

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status

from django.db.models import Count, Sum, Q
from django.utils import timezone

from accounts.models import User
from employees.models import Employee, EmployeeDocument
from leaveapp.models import LeaveRequest, LeaveBalance, LeaveType
from notifications.models import Notification

try:
    from contracts.models import Contract
except Exception:
    Contract = None

try:
    from benefits.models import EducationClaim, Dependant
except Exception:
    EducationClaim = None
    Dependant = None

try:
    from recruitment.models import Vacancy
except Exception:
    Vacancy = None


HR_ROLES = {
    User.Role.SYSTEM_ADMIN,
    User.Role.HR_MANAGER,
    User.Role.HR_OFFICER,
}

MANAGER_ROLES = HR_ROLES | {
    User.Role.LINE_MANAGER,
    User.Role.PVC,
    User.Role.ADMIN_OFFICER,
    User.Role.FINANCE_OFFICER,
}


class DashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        if user.role in HR_ROLES:
            return Response(self._hr_dashboard(user))
        if user.role in MANAGER_ROLES:
            return Response(self._manager_dashboard(user))
        return Response(self._employee_dashboard(user))

    # ------------------------------------------------------------------ HR
    def _hr_dashboard(self, user):
        today = timezone.now().date()
        year = today.year

        total_employees = Employee.objects.count()

        open_vacancies = 0
        if Vacancy is not None:
            open_vacancies = Vacancy.objects.filter(
                status__in=["PUBLISHED", "APPROVED", "SUBMITTED"]
            ).count()

        today_iso = today.isoformat()
        on_leave_today = LeaveRequest.objects.filter(
            status=LeaveRequest.Status.APPROVED,
            start_date__lte=today,
            end_date__gte=today,
        ).count()

        pending_leave = LeaveRequest.objects.exclude(
            status__in=[
                LeaveRequest.Status.APPROVED,
                LeaveRequest.Status.REJECTED,
                LeaveRequest.Status.CANCELLED,
            ]
        ).count()

        pending_claims = 0
        if EducationClaim is not None:
            pending_claims = EducationClaim.objects.filter(
                status__in=["SUBMITTED", "NEEDS_INFO", "FINANCE_PENDING"]
            ).count()

        # Alerts -------------------------------------------------------
        contracts_expiring = []
        probation_ending = []
        if Contract is not None:
            for days_ahead in [90, 60, 30]:
                target = today + timedelta(days=days_ahead)
                qs = Contract.objects.select_related(
                    "employee", "employee__user"
                ).filter(end_date=target)
                for c in qs[:50]:
                    contracts_expiring.append({
                        "employee_number": c.employee.employee_number,
                        "name": c.employee.user.full_name,
                        "end_date": c.end_date.isoformat(),
                        "days_remaining": days_ahead,
                    })

            prob_qs = Contract.objects.select_related(
                "employee", "employee__user"
            ).filter(
                probation_end_date__isnull=False,
                probation_end_date__gte=today,
                probation_end_date__lte=today + timedelta(days=30),
            )
            for c in prob_qs[:50]:
                diff = (c.probation_end_date - today).days
                probation_ending.append({
                    "employee_number": c.employee.employee_number,
                    "name": c.employee.user.full_name,
                    "probation_end_date": c.probation_end_date.isoformat(),
                    "days_remaining": diff,
                })

        retirements = []
        retirement_age = 65
        for emp in Employee.objects.select_related("user").exclude(date_of_birth__isnull=True)[:500]:
            dob = emp.date_of_birth
            if not dob:
                continue
            try:
                rdate = date(dob.year + retirement_age, dob.month, dob.day)
            except Exception:
                continue
            diff = (rdate - today).days
            if 0 <= diff <= 365:
                retirements.append({
                    "employee_number": emp.employee_number,
                    "name": emp.user.full_name,
                    "retirement_date": rdate.isoformat(),
                    "days_remaining": diff,
                })

        # Missing documents
        required_categories = [
            "NATIONAL_ID_OR_PASSPORT", "ACADEMIC_CERTIFICATES",
            "PROFESSIONAL_CERTIFICATIONS", "CV", "BANKING_DETAILS",
        ]
        missing_docs = []
        for emp in Employee.objects.select_related("user")[:200]:
            existing = set(
                EmployeeDocument.objects.filter(employee=emp, is_latest=True)
                .values_list("category", flat=True)
            )
            miss = [c for c in required_categories if c not in existing]
            if miss:
                missing_docs.append({
                    "employee_number": emp.employee_number,
                    "name": emp.user.full_name,
                    "missing": miss,
                })

        # Upcoming birthdays (next 7 days)
        upcoming_birthdays = []
        for i in range(7):
            d = today + timedelta(days=i)
            for emp in Employee.objects.select_related("user").filter(
                date_of_birth__month=d.month, date_of_birth__day=d.day
            ):
                upcoming_birthdays.append({
                    "employee_number": emp.employee_number,
                    "name": emp.user.full_name,
                    "date": d.isoformat(),
                    "days_until": i,
                })

        # Recent notifications for this user
        recent_notifications = list(
            Notification.objects.filter(user=user)
            .order_by("-created_at")[:10]
            .values("id", "title", "message", "is_read", "created_at")
        )

        return {
            "role": user.role,
            "stats": {
                "total_employees": total_employees,
                "open_vacancies": open_vacancies,
                "on_leave_today": on_leave_today,
                "pending_leave": pending_leave,
                "pending_claims": pending_claims,
            },
            "alerts": {
                "contracts_expiring": contracts_expiring,
                "probation_ending": probation_ending,
                "retirements": retirements,
                "missing_documents": missing_docs,
                "upcoming_birthdays": upcoming_birthdays,
            },
            "recent_notifications": recent_notifications,
        }

    # ----------------------------------------------------------- MANAGER
    def _manager_dashboard(self, user):
        today = timezone.now().date()

        # Team stats
        team_qs = Employee.objects.filter(line_manager=user)
        team_count = team_qs.count()

        team_on_leave = 0
        team_ids = list(team_qs.values_list("id", flat=True))
        if team_ids:
            team_on_leave = LeaveRequest.objects.filter(
                employee_id__in=team_ids,
                status=LeaveRequest.Status.APPROVED,
                start_date__lte=today,
                end_date__gte=today,
            ).count()

        pending_approvals = LeaveRequest.objects.filter(
            employee_id__in=team_ids,
            status=LeaveRequest.Status.PENDING_LM,
        ).count()

        recent_notifications = list(
            Notification.objects.filter(user=user)
            .order_by("-created_at")[:10]
            .values("id", "title", "message", "is_read", "created_at")
        )

        return {
            "role": user.role,
            "stats": {
                "team_count": team_count,
                "team_on_leave": team_on_leave,
                "pending_approvals": pending_approvals,
            },
            "recent_notifications": recent_notifications,
        }

    # ---------------------------------------------------------- EMPLOYEE
    def _employee_dashboard(self, user):
        today = timezone.now().date()
        year = today.year
        emp = getattr(user, "employee_profile", None)

        # Leave balances
        leave_balances = []
        if emp:
            for lb in LeaveBalance.objects.filter(employee=emp, year=year).select_related("leave_type"):
                leave_balances.append({
                    "leave_type": lb.leave_type.name,
                    "days_entitled": lb.days_entitled,
                    "days_used": lb.days_used,
                    "days_remaining": lb.days_remaining,
                })

        # Recent leave requests
        leave_requests = []
        if emp:
            for lr in LeaveRequest.objects.filter(employee=emp).order_by("-created_at")[:10]:
                leave_requests.append({
                    "id": lr.id,
                    "leave_type": lr.leave_type.name if lr.leave_type else "",
                    "start_date": lr.start_date.isoformat() if lr.start_date else None,
                    "end_date": lr.end_date.isoformat() if lr.end_date else None,
                    "days_requested": lr.days_requested,
                    "status": lr.status,
                    "created_at": lr.created_at.isoformat() if lr.created_at else None,
                })

        # Education claims
        claims = []
        if emp and EducationClaim is not None:
            for cl in EducationClaim.objects.filter(employee=emp).order_by("-created_at")[:10]:
                claims.append({
                    "id": cl.id,
                    "dependant_name": cl.dependant.name if cl.dependant else "",
                    "academic_year": cl.academic_year,
                    "amount_claimed": float(cl.amount_claimed) if cl.amount_claimed else 0,
                    "amount_approved": float(cl.amount_approved) if cl.amount_approved else None,
                    "status": cl.status,
                })

        # Documents
        documents = []
        if emp:
            for doc in EmployeeDocument.objects.filter(employee=emp, is_latest=True):
                documents.append({
                    "id": doc.id,
                    "category": doc.category,
                    "original_name": doc.original_name,
                    "uploaded_at": doc.uploaded_at.isoformat() if doc.uploaded_at else None,
                })

        # Profile
        profile = None
        if emp:
            profile = {
                "employee_number": emp.employee_number,
                "department": emp.department.name if emp.department else "",
                "position": emp.position.title if emp.position else "",
                "employment_status": emp.employment_status,
                "contract_type": emp.contract_type,
                "hire_date": emp.hire_date.isoformat() if emp.hire_date else None,
                "date_of_birth": emp.date_of_birth.isoformat() if emp.date_of_birth else None,
                "line_manager": emp.line_manager.full_name if emp.line_manager else None,
            }

        # Recent notifications
        recent_notifications = list(
            Notification.objects.filter(user=user)
            .order_by("-created_at")[:10]
            .values("id", "title", "message", "is_read", "created_at")
        )

        # Dependants
        dependants = []
        if emp and Dependant is not None:
            for dep in Dependant.objects.filter(employee=emp):
                dependants.append({
                    "id": dep.id,
                    "name": dep.name,
                    "relationship": dep.relationship,
                    "education_level": dep.education_level,
                    "institution_name": dep.institution_name,
                    "benefit_eligible": dep.benefit_eligible,
                })

        # Missing documents (employee's own)
        required_categories = [
            "NATIONAL_ID_OR_PASSPORT", "ACADEMIC_CERTIFICATES",
            "PROFESSIONAL_CERTIFICATIONS", "CV", "BANKING_DETAILS",
        ]
        missing_documents = []
        if emp:
            existing_cats = set(
                EmployeeDocument.objects.filter(employee=emp, is_latest=True)
                .values_list("category", flat=True)
            )
            missing_documents = [c for c in required_categories if c not in existing_cats]

        return {
            "role": user.role,
            "profile": profile,
            "leave_balances": leave_balances,
            "leave_requests": leave_requests,
            "education_claims": claims,
            "documents": documents,
            "dependants": dependants,
            "missing_documents": missing_documents,
            "recent_notifications": recent_notifications,
        }
