from rest_framework import viewsets, permissions, decorators, status
from rest_framework.response import Response
from django.http import FileResponse

from accounts.models import User
from accounts.permissions import RolePermission
from audit.mixins import AuditMixin

from .models import Contract
from .serializers import ContractSerializer, ContractGeneratorSerializer
from .generator import generate_contract_docx


class ContractViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = Contract.objects.select_related("employee", "employee__user").all()
    serializer_class = ContractSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        if user.role == User.Role.EMPLOYEE:
            emp = getattr(user, "employee_profile", None)
            return qs.filter(employee=emp) if emp else qs.none()
        if user.role == User.Role.LINE_MANAGER:
            # Direct reports only
            return qs.filter(employee__line_manager=user)
        return qs

    def get_permissions(self):
        if self.request.method in ("POST", "PUT", "PATCH", "DELETE"):
            self.allowed_roles = [User.Role.SYSTEM_ADMIN, User.Role.HR_MANAGER, User.Role.HR_OFFICER]
            return [permissions.IsAuthenticated(), RolePermission()]
        return [permissions.IsAuthenticated()]

    @decorators.action(detail=False, methods=["post"])
    def generate_contract(self, request, *args, **kwargs):
        """Generate a .docx employment contract from template."""
        # Check permissions
        if request.user.role not in [User.Role.SYSTEM_ADMIN, User.Role.HR_MANAGER, User.Role.HR_OFFICER]:
            return Response(
                {"detail": "Only HR staff can generate contracts."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = ContractGeneratorSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Generate the .docx file
            contract_bytes = generate_contract_docx(serializer.validated_data)
            
            # Create filename from employee name and dates
            employee_name = serializer.validated_data.get("employee_name", "contract").replace(" ", "_")
            start_date = serializer.validated_data.get("start_date")
            filename = f"Contract_{employee_name}_{start_date}.docx"
            
            self.audit_log("CREATE", Contract, {
                "info": "Contract template generated",
                "employee_name": employee_name
            })
            
            return FileResponse(
                contract_bytes,
                as_attachment=True,
                filename=filename,
                content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        except Exception as e:
            return Response(
                {"detail": f"Failed to generate contract: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return [permissions.IsAuthenticated()]
