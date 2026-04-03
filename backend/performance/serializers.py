from rest_framework import serializers
from .models import AppraisalTemplate, Appraisal, Goal
from employees.serializers import EmployeeSerializer
from employees.models import Employee

class AppraisalTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppraisalTemplate
        fields = ["id", "name", "schema"]

class AppraisalSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)
    employee_id = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all(), source="employee", write_only=True)
    template = AppraisalTemplateSerializer(read_only=True)
    template_id = serializers.PrimaryKeyRelatedField(queryset=AppraisalTemplate.objects.all(), source="template", write_only=True)

    class Meta:
        model = Appraisal
        fields = [
            "id", "employee", "employee_id", "template", "template_id",
            "year", "period", "self_assessment", "supervisor_feedback", "hr_notes",
            "status", "created_at",
        ]
        read_only_fields = ["status", "created_at"]

class GoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goal
        fields = ["id", "appraisal", "description", "progress_note"]
