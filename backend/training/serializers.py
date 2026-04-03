from rest_framework import serializers
from employees.serializers import EmployeeMiniSerializer, DepartmentSerializer
from employees.models import Employee, Department
from .models import Competency, EmployeeCompetency, TrainingProgram, TrainingNeed, EmployeeTraining


class CompetencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Competency
        fields = ["id", "name", "category", "description"]


class EmployeeCompetencySerializer(serializers.ModelSerializer):
    employee = EmployeeMiniSerializer(read_only=True)
    employee_id = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all(), source="employee", write_only=True)
    competency = CompetencySerializer(read_only=True)
    competency_id = serializers.PrimaryKeyRelatedField(queryset=Competency.objects.all(), source="competency", write_only=True)

    class Meta:
        model = EmployeeCompetency
        fields = ["id", "employee", "employee_id", "competency", "competency_id", "level", "last_assessed", "notes"]


class TrainingProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingProgram
        fields = ["id", "title", "provider", "category", "description", "start_date", "end_date", "estimated_cost"]


class TrainingNeedSerializer(serializers.ModelSerializer):
    employee = EmployeeMiniSerializer(read_only=True)
    employee_id = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all(), source="employee", write_only=True, required=False, allow_null=True)
    department = DepartmentSerializer(read_only=True)
    department_id = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all(), source="department", write_only=True, required=False, allow_null=True)
    competency = CompetencySerializer(read_only=True)
    competency_id = serializers.PrimaryKeyRelatedField(queryset=Competency.objects.all(), source="competency", write_only=True, required=False, allow_null=True)
    identified_by_email = serializers.CharField(source="identified_by.email", read_only=True)

    class Meta:
        model = TrainingNeed
        fields = [
            "id",
            "employee",
            "employee_id",
            "department",
            "department_id",
            "competency",
            "competency_id",
            "description",
            "priority",
            "identified_by",
            "identified_by_email",
            "identified_at",
        ]
        read_only_fields = ["identified_by", "identified_at", "identified_by_email"]

    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user and request.user.is_authenticated:
            validated_data["identified_by"] = request.user
        return super().create(validated_data)


class EmployeeTrainingSerializer(serializers.ModelSerializer):
    employee = EmployeeMiniSerializer(read_only=True)
    employee_id = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all(), source="employee", write_only=True)
    program = TrainingProgramSerializer(read_only=True)
    program_id = serializers.PrimaryKeyRelatedField(queryset=TrainingProgram.objects.all(), source="program", write_only=True)
    recorded_by_email = serializers.CharField(source="recorded_by.email", read_only=True)

    class Meta:
        model = EmployeeTraining
        fields = [
            "id",
            "employee",
            "employee_id",
            "program",
            "program_id",
            "status",
            "cost",
            "outcome",
            "certificate",
            "recorded_by",
            "recorded_by_email",
            "recorded_at",
        ]
        read_only_fields = ["recorded_by", "recorded_at", "recorded_by_email"]

    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user and request.user.is_authenticated:
            validated_data["recorded_by"] = request.user
        return super().create(validated_data)
