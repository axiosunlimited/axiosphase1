from rest_framework import serializers
from employees.models import Employee
from employees.serializers import EmployeeMiniSerializer
from .models import (
    ApprovalProcessConfig,
    Policy,
    PolicyAcknowledgement,
    DisciplinaryCase,
    Grievance,
    ComplianceItem,
)


class ApprovalProcessConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApprovalProcessConfig
        fields = ["id", "process_code", "name", "description", "allowed_roles", "is_active", "updated_at"]
        read_only_fields = ["updated_at"]


class PolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = Policy
        fields = [
            "id", "title", "description", "document", "version",
            "effective_date", "is_active", "created_at", "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class PolicyAcknowledgementSerializer(serializers.ModelSerializer):
    employee = EmployeeMiniSerializer(read_only=True)
    employee_id = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(), source="employee", write_only=True,
    )
    policy_title = serializers.CharField(source="policy.title", read_only=True)

    class Meta:
        model = PolicyAcknowledgement
        fields = [
            "id", "policy", "policy_title", "employee", "employee_id",
            "acknowledged_at",
        ]
        read_only_fields = ["acknowledged_at"]


class DisciplinaryCaseSerializer(serializers.ModelSerializer):
    employee = EmployeeMiniSerializer(read_only=True)
    employee_id = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(), source="employee", write_only=True,
    )

    class Meta:
        model = DisciplinaryCase
        fields = [
            "id", "employee", "employee_id", "case_description", "date",
            "outcome", "supporting_document", "created_at", "created_by",
        ]
        read_only_fields = ["created_at", "created_by"]

    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user:
            validated_data["created_by"] = request.user
        return super().create(validated_data)


class GrievanceSerializer(serializers.ModelSerializer):
    employee = EmployeeMiniSerializer(read_only=True)
    employee_id = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(), source="employee", write_only=True,
    )

    class Meta:
        model = Grievance
        fields = [
            "id", "employee", "employee_id", "subject", "description",
            "date_filed", "status", "resolution", "created_at", "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class ComplianceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplianceItem
        fields = [
            "id", "title", "description", "category", "due_date",
            "status", "notes", "created_at", "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]
