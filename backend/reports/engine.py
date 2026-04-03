from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from django.db.models import Count, Avg, Sum, Min, Max, QuerySet

from employees.models import Employee
from leaveapp.models import LeaveRequest, LeaveBalance
from recruitment.models import Vacancy, Applicant
from performance.models import Appraisal

# Optional apps (installed in this repo)
try:
    from employees.models import EmploymentHistory
except Exception:
    EmploymentHistory = None

try:
    from training.models import EmployeeTraining
except Exception:
    EmployeeTraining = None

try:
    from workforce.models import EstablishmentItem, Separation
except Exception:
    EstablishmentItem = None
    Separation = None


DATASET_MAP = {
    "EMPLOYEES": Employee,
    "EMPLOYMENT_HISTORY": EmploymentHistory,
    "LEAVE_REQUESTS": LeaveRequest,
    "LEAVE_BALANCES": LeaveBalance,
    "VACANCIES": Vacancy,
    "APPLICANTS": Applicant,
    "APPRAISALS": Appraisal,
    "TRAINING_RECORDS": EmployeeTraining,
    "ESTABLISHMENT": EstablishmentItem,
    "SEPARATIONS": Separation,
}


SUPPORTED_FILTER_OPS = {
    "eq", "ne", "lt", "lte", "gt", "gte",
    "contains", "icontains",
    "in", "range",
    "isnull",
}

SUPPORTED_AGG_OPS = {
    "count", "sum", "avg", "min", "max",
}


@dataclass
class ReportResult:
    rows: List[Dict[str, Any]]
    meta: Dict[str, Any]


def _get_model(dataset_key: str):
    model = DATASET_MAP.get(dataset_key)
    if model is None:
        raise ValueError(f"Unknown or unavailable dataset: {dataset_key}")
    return model


def _validate_field(model, field_path: str) -> None:
    """Validate a Django ORM field path (including related paths)."""
    parts = field_path.split("__")
    m = model
    for i, part in enumerate(parts):
        try:
            f = m._meta.get_field(part)
        except Exception:
            raise ValueError(f"Invalid field path: {field_path}")
        if i < len(parts) - 1:
            # traverse relations
            rel_model = getattr(f, "related_model", None)
            if rel_model is None:
                raise ValueError(f"Invalid field path: {field_path}")
            m = rel_model


def _apply_filters(qs: QuerySet, model, filters: List[Dict[str, Any]]) -> QuerySet:
    for flt in filters or []:
        field = flt.get("field")
        op = flt.get("op")
        value = flt.get("value")
        if not field or op not in SUPPORTED_FILTER_OPS:
            raise ValueError("Invalid filter")
        _validate_field(model, field)

        if op == "eq":
            qs = qs.filter(**{field: value})
        elif op == "ne":
            qs = qs.exclude(**{field: value})
        elif op in {"lt", "lte", "gt", "gte"}:
            qs = qs.filter(**{f"{field}__{op}": value})
        elif op in {"contains", "icontains"}:
            qs = qs.filter(**{f"{field}__{op}": value})
        elif op == "in":
            if not isinstance(value, list):
                raise ValueError("Filter 'in' expects a list")
            qs = qs.filter(**{f"{field}__in": value})
        elif op == "range":
            if not (isinstance(value, list) and len(value) == 2):
                raise ValueError("Filter 'range' expects [start, end]")
            qs = qs.filter(**{f"{field}__range": (value[0], value[1])})
        elif op == "isnull":
            qs = qs.filter(**{f"{field}__isnull": bool(value)})
    return qs


def _apply_group_and_aggs(qs: QuerySet, model, group_by: List[str], aggs: List[Dict[str, Any]]) -> Tuple[QuerySet, List[str]]:
    group_by = group_by or []
    aggs = aggs or []

    for gb in group_by:
        _validate_field(model, gb)

    annotations = {}
    out_fields = list(group_by)

    for agg in aggs:
        op = (agg.get("op") or "").lower()
        field = agg.get("field")
        alias = agg.get("as") or f"{op}_{field or 'value'}"
        if op not in SUPPORTED_AGG_OPS:
            raise ValueError("Invalid aggregation")
        if field and field != "*":
            _validate_field(model, field)

        if op == "count":
            annotations[alias] = Count(field if field and field != "*" else "id")
        elif op == "sum":
            annotations[alias] = Sum(field)
        elif op == "avg":
            annotations[alias] = Avg(field)
        elif op == "min":
            annotations[alias] = Min(field)
        elif op == "max":
            annotations[alias] = Max(field)
        out_fields.append(alias)

    if group_by:
        qs = qs.values(*group_by).annotate(**annotations)
    elif annotations:
        # aggregate without grouping => single row
        qs = qs.aggregate(**annotations)
        return qs, out_fields

    return qs, out_fields


def run_custom_report(dataset_key: str, definition: Dict[str, Any]) -> ReportResult:
    model = _get_model(dataset_key)

    fields = definition.get("fields") or []
    filters = definition.get("filters") or []
    order_by = definition.get("order_by") or []
    group_by = definition.get("group_by") or []
    aggs = definition.get("aggregations") or []
    limit = int(definition.get("limit") or 1000)

    for f in fields:
        _validate_field(model, f)
    for ob in order_by:
        ob_field = ob[1:] if ob.startswith("-") else ob
        _validate_field(model, ob_field)

    qs = model.objects.all()
    qs = _apply_filters(qs, model, filters)

    if group_by or aggs:
        qs2, out_fields = _apply_group_and_aggs(qs, model, group_by, aggs)
        if isinstance(qs2, dict):
            # single row aggregate
            return ReportResult(rows=[qs2], meta={"dataset": dataset_key, "fields": list(qs2.keys()), "group_by": [], "aggregations": aggs})

        if order_by:
            qs2 = qs2.order_by(*order_by)
        qs2 = qs2[:max(1, min(limit, 10000))]
        rows = list(qs2)
        return ReportResult(rows=rows, meta={"dataset": dataset_key, "fields": out_fields, "group_by": group_by, "aggregations": aggs})

    # Simple list
    if fields:
        qs = qs.values(*fields)
    if order_by:
        qs = qs.order_by(*order_by)
    qs = qs[:max(1, min(limit, 10000))]
    rows = list(qs)
    meta = {"dataset": dataset_key, "fields": fields or "__all__", "count": len(rows)}
    return ReportResult(rows=rows, meta=meta)
