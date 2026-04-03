from rest_framework import serializers
from employees.serializers import EmployeeMiniSerializer
from employees.models import Employee
from .models import Contract


class ContractSerializer(serializers.ModelSerializer):
    employee = EmployeeMiniSerializer(read_only=True)
    employee_id = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all(), source="employee", write_only=True)

    class Meta:
        model = Contract
        fields = ["id", "employee", "employee_id", "start_date", "end_date", "probation_end_date", "contract_type", "created_at", "is_active"]
        read_only_fields = ["created_at", "is_active"]

class ContractGeneratorSerializer(serializers.Serializer):
    """Serializer for generating an employment contract .docx file."""
    
    employee_name = serializers.CharField(max_length=255, required=True)
    national_id = serializers.CharField(max_length=100, required=True)
    address = serializers.CharField(max_length=255, required=True)
    mobile = serializers.CharField(max_length=20, required=True)
    position = serializers.CharField(max_length=255, required=True)
    department = serializers.CharField(max_length=255, required=True)
    grade = serializers.CharField(max_length=50, required=False, allow_blank=True)
    contract_type = serializers.CharField(max_length=50, required=False, default="Fixed Term")
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=True)
    probation_months = serializers.IntegerField(required=False, default=3)
    basic_salary = serializers.DecimalField(max_digits=12, decimal_places=2, required=True)
    transport_allowance = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, default=120)
    housing_allowance = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, default=175)
    bonus_enabled = serializers.BooleanField(required=False, default=True)
    medical_aid_enabled = serializers.BooleanField(required=False, default=True)
    school_fees_enabled = serializers.BooleanField(required=False, default=True)
    reporting_to = serializers.CharField(max_length=255, required=False, default="the Dean of your Department")
    signed_by = serializers.CharField(max_length=255, required=False, allow_blank=True)
    witness_name = serializers.CharField(max_length=255, required=False, default="Human Resources Officer")
    
    def validate(self, data):
        """Ensure end_date is after start_date."""
        if data.get('end_date') <= data.get('start_date'):
            raise serializers.ValidationError("End date must be after start date.")
        return data