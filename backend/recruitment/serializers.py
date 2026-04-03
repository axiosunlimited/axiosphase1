from rest_framework import serializers
from .models import Vacancy, Applicant, Interview, Appointment
from employees.serializers import DepartmentSerializer, PositionSerializer
from employees.models import Department, Position

class VacancySerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)
    department_id = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all(), source="department", write_only=True)
    position = PositionSerializer(read_only=True)
    position_id = serializers.PrimaryKeyRelatedField(queryset=Position.objects.all(), source="position", write_only=True)

    class Meta:
        model = Vacancy
        fields = ["id", "title", "description", "status", "department", "department_id", "position", "position_id", "created_at", "closing_date"]
        read_only_fields = ["created_at"]

class ApplicantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Applicant
        fields = ["id", "vacancy", "first_name", "last_name", "email", "phone", "cv", "status", "created_at"]
        read_only_fields = ["created_at"]

class InterviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interview
        fields = ["id", "applicant", "scheduled_at", "location", "notes", "outcome"]

class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ["id", "applicant", "start_date", "salary_note", "created_at"]
        read_only_fields = ["created_at"]
