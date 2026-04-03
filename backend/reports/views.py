from __future__ import annotations

from rest_framework import viewsets, permissions, decorators, status
from rest_framework.response import Response
from django.http import FileResponse

from accounts.permissions import RolePermission
from accounts.models import User
from audit.mixins import AuditMixin

from .models import ReportDefinition
from .serializers import ReportDefinitionSerializer
from .engine import run_custom_report
from .predefined import PREDEFINED_REPORTS, run_predefined
from .exporters import to_xlsx_table, to_pdf_table, to_pdf_summary


class ReportDefinitionViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = ReportDefinition.objects.select_related("created_by").all()
    serializer_class = ReportDefinitionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        if user.role in [User.Role.SYSTEM_ADMIN, User.Role.HR_MANAGER, User.Role.HR_OFFICER]:
            return qs
        # Other roles can only see their own (if ever created)
        return qs.filter(created_by=user)

    def get_permissions(self):
        if self.request.method in ("POST", "PUT", "PATCH", "DELETE"):
            self.allowed_roles = [User.Role.SYSTEM_ADMIN, User.Role.HR_MANAGER, User.Role.HR_OFFICER]
            return [permissions.IsAuthenticated(), RolePermission()]
        return [permissions.IsAuthenticated()]

    @decorators.action(detail=True, methods=["post"])
    def run(self, request, *args, **kwargs):
        rd = self.get_object()
        try:
            result = run_custom_report(rd.dataset, rd.definition or {})
            self.audit_log("READ", rd, {"info": "Report run"})
            return Response({"definition": ReportDefinitionSerializer(rd).data, "meta": result.meta, "rows": result.rows})
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @decorators.action(detail=True, methods=["get"])
    def export(self, request, *args, **kwargs):
        rd = self.get_object()
        fmt = (request.query_params.get("export_format") or request.query_params.get("format") or "xlsx").lower()
        try:
            result = run_custom_report(rd.dataset, rd.definition or {})
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        title = rd.name
        if fmt == "xlsx":
            buf = to_xlsx_table(result.rows, title=title)
            filename = f"report_{rd.id}.xlsx"
            self.audit_log("READ", rd, {"info": "Report exported", "format": "xlsx"})
            return FileResponse(buf, as_attachment=True, filename=filename)
        if fmt == "pdf":
            buf = to_pdf_table(result.rows, title=title)
            filename = f"report_{rd.id}.pdf"
            self.audit_log("READ", rd, {"info": "Report exported", "format": "pdf"})
            return FileResponse(buf, as_attachment=True, filename=filename)

        return Response({"detail": "Unsupported format. Use format=xlsx or format=pdf"}, status=status.HTTP_400_BAD_REQUEST)


class PredefinedReportViewSet(viewsets.ViewSet):
    allowed_roles = [
        User.Role.SYSTEM_ADMIN,
        User.Role.HR_MANAGER,
        User.Role.HR_OFFICER,
        User.Role.FINANCE_OFFICER,
        User.Role.LINE_MANAGER,
    ]
    permission_classes = [permissions.IsAuthenticated, RolePermission]

    def list(self, request, *args, **kwargs):
        items = []
        for key, meta in PREDEFINED_REPORTS.items():
            items.append({"key": key, **meta})
        return Response(items)

    def retrieve(self, request, pk=None, *args, **kwargs):
        meta = PREDEFINED_REPORTS.get(pk)
        if not meta:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"key": pk, **meta})

    @decorators.action(detail=True, methods=["post"], url_name="predefined-run", url_path="run")
    def run(self, request, pk=None, *args, **kwargs):
        params = request.data or {}
        try:
            data = run_predefined(pk, params)
            return Response(data)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @decorators.action(detail=True, methods=["get"], url_name="predefined-export", url_path="export")
    def export(self, request, pk=None, *args, **kwargs):
        fmt = (request.query_params.get("export_format") or request.query_params.get("format") or "pdf").lower()
        params = dict(request.query_params)
        # flatten: keep first value
        params = {k: (v[0] if isinstance(v, list) else v) for k, v in params.items()}
        try:
            data = run_predefined(pk, params)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        title = PREDEFINED_REPORTS.get(pk, {}).get("name", "Report")

        if fmt == "pdf":
            buf = to_pdf_summary(data, title=title)
            filename = f"{pk}.pdf"
            return FileResponse(buf, as_attachment=True, filename=filename)

        if fmt == "xlsx":
            # For summary exports, make a flattened table of key/value pairs
            rows = []
            metrics = data.get("metrics") or {}
            if isinstance(metrics, dict):
                for k, v in metrics.items():
                    rows.append({"metric": k, "value": v})
            buf = to_xlsx_table(rows, title=title)
            filename = f"{pk}.xlsx"
            return FileResponse(buf, as_attachment=True, filename=filename)

        return Response({"detail": "Unsupported format. Use format=pdf or format=xlsx"}, status=status.HTTP_400_BAD_REQUEST)


class AnalyticsDashboardViewSet(viewsets.ViewSet):
    """Role-based analytics dashboards."""
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        """List available analytics dashboard types for current user."""
        user = request.user
        available = ["employee"]
        
        if user.role in [User.Role.SYSTEM_ADMIN]:
            available = ["system_admin", "hr_manager", "line_manager", "finance_officer", "employee"]
        elif user.role in [User.Role.HR_MANAGER, User.Role.HR_OFFICER]:
            available = ["hr_manager", "employee"]
        elif user.role == User.Role.LINE_MANAGER:
            available = ["line_manager", "employee"]
        elif user.role == User.Role.FINANCE_OFFICER:
            available = ["finance_officer", "employee"]
        elif user.role == User.Role.ADMIN_OFFICER:
            available = ["hr_manager", "employee"]
        
        return Response({
            "user_role": user.role,
            "available_dashboards": available
        })

    @decorators.action(detail=False, methods=["get"])
    def my_dashboard(self, request, *args, **kwargs):
        """Get the appropriate dashboard for the current user."""
        from .analytics import get_analytics_dashboard
        
        params = dict(request.query_params)
        try:
            dashboard = get_analytics_dashboard(request.user, params)
            return Response(dashboard)
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
