from __future__ import annotations

from datetime import date

from django.utils import timezone

from .models import EducationAssistancePolicy, Dependant, EducationClaim


def recalc_dependant_eligibility(employee):
    """Mark only up to policy.max_children_per_employee CHILD dependants as eligible.

    Also applies max_child_age and allowed_levels (if configured).
    """
    policy = EducationAssistancePolicy.active()
    max_children = policy.max_children_per_employee or 2

    deps = list(Dependant.objects.filter(employee=employee, relationship=Dependant.Relationship.CHILD).order_by("created_at", "id"))

    today = timezone.now().date()

    allowed_ids = {d.id for d in deps[:max_children]}

    for i, d in enumerate(deps):
        eligible = True
        reason = ""

        if d.id not in allowed_ids:
            eligible = False
            reason = f"Policy limit exceeded (max {max_children} children)."

        if eligible and policy.max_child_age:
            # Approx age in years
            age = today.year - d.date_of_birth.year - ((today.month, today.day) < (d.date_of_birth.month, d.date_of_birth.day))
            if age > policy.max_child_age:
                eligible = False
                reason = f"Child age exceeds policy maximum ({policy.max_child_age})."

        if eligible and policy.allowed_levels:
            if d.education_level not in policy.allowed_levels:
                eligible = False
                reason = "Education level not covered by policy."

        if d.benefit_eligible != eligible or d.ineligible_reason != reason:
            d.benefit_eligible = eligible
            d.ineligible_reason = reason
            d.save(update_fields=["benefit_eligible", "ineligible_reason"])


def approved_claims_for_employee_in_period(employee, academic_year: int, period_type: str, period_label: str) -> int:
    # Policy limit is per-child, so count distinct dependants with an approved claim.
    return (
        EducationClaim.objects.filter(
            employee=employee,
            academic_year=academic_year,
            period_type=period_type,
            period_label=period_label,
            status__in=[EducationClaim.Status.FINANCE_PENDING, EducationClaim.Status.PAID],
        )
        .values("dependant_id")
        .distinct()
        .count()
    )
