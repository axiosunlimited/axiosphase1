from rest_framework import serializers
from .models import LeaveType, LeaveBalance, LeaveRequest, PublicHoliday
from employees.serializers import EmployeeMiniSerializer
from employees.models import Employee
from .utils import business_days

class LeaveTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveType
        fields = ["id", "name", "default_days_per_year", "requires_approval"]

class PublicHolidaySerializer(serializers.ModelSerializer):
    class Meta:
        model = PublicHoliday
        fields = ["id", "date", "name"]

class LeaveBalanceSerializer(serializers.ModelSerializer):
    employee = EmployeeMiniSerializer(read_only=True)
    employee_id = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all(), source="employee", write_only=True)
    leave_type = LeaveTypeSerializer(read_only=True)
    leave_type_id = serializers.PrimaryKeyRelatedField(queryset=LeaveType.objects.all(), source="leave_type", write_only=True)
    days_remaining = serializers.IntegerField(read_only=True)

    class Meta:
        model = LeaveBalance
        fields = ["id", "employee", "employee_id", "leave_type", "leave_type_id", "year", "days_entitled", "days_used", "days_remaining"]

class LeaveRequestSerializer(serializers.ModelSerializer):
    employee = EmployeeMiniSerializer(read_only=True)
    employee_id = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all(), source="employee", write_only=True, required=False)
    leave_type = LeaveTypeSerializer(read_only=True)
    leave_type_id = serializers.PrimaryKeyRelatedField(queryset=LeaveType.objects.all(), source="leave_type", write_only=True)
    line_manager_email = serializers.CharField(source="line_manager.email", read_only=True)
    hr_officer_email = serializers.CharField(source="hr_officer.email", read_only=True)
    pvc_officer_email = serializers.CharField(source="pvc_officer.email", read_only=True)
    admin_officer_email = serializers.CharField(source="admin_officer.email", read_only=True)
    finance_officer_email = serializers.CharField(source="finance_officer.email", read_only=True)
    days_requested = serializers.IntegerField(read_only=True)

    class Meta:
        model = LeaveRequest
        fields = [
            "id",
            "employee",
            "employee_id",
            "leave_type",
            "leave_type_id",
            "start_date",
            "end_date",
            "days_requested",
            "status",
            "reason",
            "decision_note",
            "created_at",
            "line_manager",
            "line_manager_email",
            "hr_officer",
            "hr_officer_email",
            "pvc_officer",
            "pvc_officer_email",
            "admin_officer",
            "admin_officer_email",
            "finance_officer",
            "finance_officer_email",
            "supporting_document",
            "approved_at",
        ]
        read_only_fields = [
            "status",
            "created_at",
            "line_manager",
            "hr_officer",
            "pvc_officer",
            "admin_officer",
            "finance_officer",
            "line_manager_email",
            "hr_officer_email",
            "pvc_officer_email",
            "admin_officer_email",
            "finance_officer_email",
            "approved_at",
        ]

    def validate(self, attrs):
        start = attrs.get("start_date")
        end = attrs.get("end_date")
        if end and start and end < start:
            raise serializers.ValidationError("end_date must be >= start_date")
        return attrs

    def create(self, validated_data):
        holidays = set(PublicHoliday.objects.values_list("date", flat=True))
        validated_data["days_requested"] = business_days(validated_data["start_date"], validated_data["end_date"], holidays)
        return super().create(validated_data)
