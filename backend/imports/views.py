from __future__ import annotations

from rest_framework import viewsets, permissions, decorators, status
from rest_framework.response import Response
from django.http import FileResponse
from io import BytesIO
import csv

from accounts.models import User
from accounts.permissions import RolePermission
from audit.mixins import AuditMixin

from .models import ImportJob
from .serializers import ImportJobSerializer
from .utils import parse_rows, apply_mapping
from .validators import (
    validate_employees,
    commit_employees,
    validate_leave_balances,
    commit_leave_balances,
    validate_contracts,
    commit_contracts,
)


TEMPLATES = {
    ImportJob.Kind.EMPLOYEES: [
        "employee_number",
        "first_name",
        "last_name",
        "national_id/passport_number",
        "position",
        "grade",
        "school",
        "department",
        "start_date",
        "end-date",
        "contract_type",
        "date_of_birth",
        "email",
        "title",
        "gender",
    ],
    ImportJob.Kind.LEAVE_BALANCES: [
        "employee_number",
        "leave_type",
        "year",
        "days_entitled",
        "days_used",
    ],
    ImportJob.Kind.CONTRACTS: [
        "employee_number",
        "start_date",
        "end_date",
        "probation_end_date",
        "contract_type",
    ],
}


class ImportJobViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = ImportJob.objects.select_related("created_by").all()
    serializer_class = ImportJobSerializer
    allowed_roles = [User.Role.SYSTEM_ADMIN, User.Role.HR_MANAGER, User.Role.HR_OFFICER]
    permission_classes = [permissions.IsAuthenticated, RolePermission]

    def perform_create(self, serializer):
        obj = serializer.save(created_by=self.request.user)
        # AuditMixin normally handles this, but we override perform_create.
        self.audit_log("CREATE", obj, {"kind": obj.kind, "status": obj.status, "info": "Import uploaded"})
        return obj

    @decorators.action(detail=False, methods=["get"], url_path="templates/(?P<kind>[^/.]+)")
    def template(self, request, *args, kind=None, **kwargs):
        kind = (kind or "").upper()
        if kind not in TEMPLATES:
            return Response({"detail": "Unknown kind."}, status=status.HTTP_400_BAD_REQUEST)

        fmt = (request.query_params.get("format") or "csv").lower()
        headers = TEMPLATES[kind]

        if fmt == "csv":
            buf = BytesIO()
            w = csv.writer(buf)
            w.writerow(headers)
            w.writerow(["" for _ in headers])
            buf.seek(0)
            filename = f"template_{kind.lower()}.csv"
            return FileResponse(buf, as_attachment=True, filename=filename)

        # xlsx
        if fmt == "xlsx":
            import openpyxl
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.append(headers)
            ws.append(["" for _ in headers])
            out = BytesIO()
            wb.save(out)
            out.seek(0)
            filename = f"template_{kind.lower()}.xlsx"
            return FileResponse(out, as_attachment=True, filename=filename)

        return Response({"detail": "Unsupported format. Use csv or xlsx."}, status=status.HTTP_400_BAD_REQUEST)

    @decorators.action(detail=False, methods=["post"], url_path="preview")
    def preview(self, request, *args, **kwargs):
        kind = (request.data.get("kind") or "").upper()
        if kind not in TEMPLATES:
            return Response({"detail": "Unknown kind."}, status=status.HTTP_400_BAD_REQUEST)

        upload = request.FILES.get("file")
        if not upload:
            return Response({"detail": "file is required"}, status=status.HTTP_400_BAD_REQUEST)

        mapping = request.data.get("mapping")
        if isinstance(mapping, str):
            import json
            try:
                mapping = json.loads(mapping)
            except Exception:
                mapping = {}
        if not isinstance(mapping, dict):
            mapping = {}

        headers, rows = parse_rows(upload)
        mapped_rows = [apply_mapping(r, mapping) for r in rows]

        if kind == ImportJob.Kind.EMPLOYEES:
            cleaned, errors = validate_employees(mapped_rows)
        elif kind == ImportJob.Kind.LEAVE_BALANCES:
            cleaned, errors = validate_leave_balances(mapped_rows)
        else:
            cleaned, errors = validate_contracts(mapped_rows)

        job = ImportJob.objects.create(
            kind=kind,
            upload=upload,
            mapping=mapping,
            status=ImportJob.Status.PREVIEWED,
            preview_rows=cleaned[:50],
            errors=errors,
            created_by=request.user,
        )
        self.audit_log("CREATE", job, {"info": "Import preview created", "kind": kind})
        return Response({"job": ImportJobSerializer(job).data, "errors": errors, "preview_rows": cleaned[:50]})

    @decorators.action(detail=True, methods=["post"], url_path="commit")
    def commit(self, request, *args, pk=None, **kwargs):
        job = self.get_object()
        if job.status not in [ImportJob.Status.PREVIEWED, ImportJob.Status.UPLOADED]:
            return Response({"detail": f"Cannot commit in status {job.status}"}, status=status.HTTP_400_BAD_REQUEST)

        # Re-parse and revalidate from stored upload for safety
        upload = job.upload.open("rb")
        headers, rows = parse_rows(upload)
        mapped_rows = [apply_mapping(r, job.mapping or {}) for r in rows]

        if job.kind == ImportJob.Kind.EMPLOYEES:
            cleaned, errors = validate_employees(mapped_rows)
            if errors:
                job.status = ImportJob.Status.FAILED
                job.errors = errors
                job.save(update_fields=["status", "errors"])
                return Response({"detail": "Validation errors", "errors": errors}, status=status.HTTP_400_BAD_REQUEST)
            result = commit_employees(cleaned, creator=request.user)
        elif job.kind == ImportJob.Kind.LEAVE_BALANCES:
            cleaned, errors = validate_leave_balances(mapped_rows)
            if errors:
                job.status = ImportJob.Status.FAILED
                job.errors = errors
                job.save(update_fields=["status", "errors"])
                return Response({"detail": "Validation errors", "errors": errors}, status=status.HTTP_400_BAD_REQUEST)
            result = commit_leave_balances(cleaned)
        else:
            cleaned, errors = validate_contracts(mapped_rows)
            if errors:
                job.status = ImportJob.Status.FAILED
                job.errors = errors
                job.save(update_fields=["status", "errors"])
                return Response({"detail": "Validation errors", "errors": errors}, status=status.HTTP_400_BAD_REQUEST)
            result = commit_contracts(cleaned)

        job.status = ImportJob.Status.COMMITTED
        job.save(update_fields=["status"])
        self.audit_log("UPDATE", job, {"info": "Import committed", **result})
        return Response({"detail": "Committed", **result})
