from rest_framework import serializers
from employees.serializers import DepartmentSerializer, PositionSerializer, EmployeeMiniSerializer
from employees.models import Department, Position, Employee
from .models import EstablishmentItem, Separation


class EstablishmentItemSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)
    department_id = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all(), source="department", write_only=True)
    position = PositionSerializer(read_only=True)
    position_id = serializers.PrimaryKeyRelatedField(queryset=Position.objects.all(), source="position", write_only=True)

    class Meta:
        model = EstablishmentItem
        fields = ["id", "year", "department", "department_id", "position", "position_id", "budgeted_headcount"]


class SeparationSerializer(serializers.ModelSerializer):
    employee = EmployeeMiniSerializer(read_only=True)
    employee_id = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all(), source="employee", write_only=True)

    class Meta:
        model = Separation
        fields = ["id", "employee", "employee_id", "separation_date", "separation_type", "reason"]
