from rest_framework import serializers
from .models import Department, Position, Employee, Qualification, EmployeeDocument, EmploymentHistory
from accounts.serializers import UserSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["id", "name", "code"]

class PositionSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)
    department_id = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all(), source="department", write_only=True)
    class Meta:
        model = Position
        fields = ["id", "title", "is_academic", "department", "department_id"]

class QualificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Qualification
        fields = ["id", "name", "institution", "year_obtained"]


class EmployeeMiniSerializer(serializers.ModelSerializer):
    email = serializers.CharField(source="user.email", read_only=True)
    full_name = serializers.CharField(source="user.full_name", read_only=True)

    class Meta:
        model = Employee
        fields = ["id", "employee_number", "email", "full_name"]


class QualificationCRUDSerializer(serializers.ModelSerializer):
    employee = EmployeeMiniSerializer(read_only=True)
    employee_id = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all(), source="employee", write_only=True)

    class Meta:
        model = Qualification
        fields = ["id", "employee", "employee_id", "name", "institution", "year_obtained"]

class EmployeeDocumentSerializer(serializers.ModelSerializer):
    employee = EmployeeMiniSerializer(read_only=True)
    employee_id = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all(), source="employee", write_only=True, required=False)
    file = serializers.FileField(write_only=True, required=True)
    class Meta:
        model = EmployeeDocument
        fields = [
            "id",
            "employee",
            "employee_id",
            "category",
            "file",
            "original_name",
            "content_type",
            "size_bytes",
            "version",
            "is_latest",
            "uploaded_by",
            "uploaded_at",
        ]
        read_only_fields = ["original_name", "content_type", "size_bytes", "version", "is_latest", "uploaded_by", "uploaded_at"]

    def create(self, validated_data):
        from django.core.files.base import ContentFile
        import uuid
        from config.crypto import encrypt_bytes

        upload = validated_data.pop("file")
        raw = upload.read()
        encrypted = encrypt_bytes(raw)

        # versioning: mark previous as not latest and increment
        employee = validated_data["employee"]
        category = validated_data["category"]
        prev = EmployeeDocument.objects.filter(employee=employee, category=category, is_latest=True).order_by("-version").first()
        version = 1
        if prev:
            version = (prev.version or 1) + 1
            EmployeeDocument.objects.filter(employee=employee, category=category, is_latest=True).update(is_latest=False)

        validated_data["original_name"] = upload.name
        validated_data["content_type"] = getattr(upload, "content_type", "") or ""
        validated_data["size_bytes"] = getattr(upload, "size", 0) or len(raw)
        validated_data["version"] = version
        validated_data["is_latest"] = True
        request = self.context.get("request")
        validated_data["uploaded_by"] = getattr(request, "user", None)

        obj = EmployeeDocument(**validated_data)
        name = f"{uuid.uuid4().hex}.enc"
        obj.encrypted_file.save(name, ContentFile(encrypted), save=False)
        obj.save()
        return obj

    def validate_file(self, f):
        from pathlib import Path
        from django.conf import settings
        from system.models import SystemSetting

        max_mb = settings.DOCUMENTS_MAX_FILE_SIZE_MB
        # allow override via system setting
        override = SystemSetting.get_value("documents.max_file_size_mb")
        try:
            if override is not None:
                max_mb = int(override if not isinstance(override, dict) else override.get("value"))
        except Exception:
            pass
        max_bytes = int(max_mb) * 1024 * 1024
        if getattr(f, "size", 0) and f.size > max_bytes:
            raise serializers.ValidationError(f"File too large. Max {max_mb} MB.")

        allowed_exts = getattr(settings, "DOCUMENTS_ALLOWED_EXTENSIONS", ["pdf", "doc", "docx", "jpg", "jpeg", "png", "gif", "bmp", "webp", "img", "tiff", "txt", "xlsx", "xls", "csv", "pptx", "ppt"])
        norm = []
        for e in allowed_exts:
            e = (e or "").lower().strip()
            if not e:
                continue
            norm.append(e if e.startswith(".") else f".{e}")
        ext = Path(f.name or "").suffix.lower()
        if ext not in norm:
            raise serializers.ValidationError("Unsupported file type.")
        return f

class EmployeeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source="user", write_only=True)
    department = DepartmentSerializer(read_only=True)
    department_id = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all(), source="department", write_only=True)
    position = PositionSerializer(read_only=True)
    position_id = serializers.PrimaryKeyRelatedField(queryset=Position.objects.all(), source="position", write_only=True)
    qualifications = QualificationSerializer(many=True, read_only=True)

    line_manager_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source="line_manager", write_only=True, required=False, allow_null=True)
    line_manager = UserSerializer(read_only=True)

    class Meta:
        model = Employee
        fields = [
            "id", "user", "user_id",
            "employee_number",
            "department", "department_id",
            "position", "position_id",
            "employment_status", "contract_type", "hire_date", "end_date",
            "date_of_birth",
            "line_manager",
            "line_manager_id",
            "title", "gender", "grade", "school",
            "national_id", "phone", "address",
            "qualifications",
        ]


class EmploymentHistorySerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)
    position = PositionSerializer(read_only=True)

    class Meta:
        model = EmploymentHistory
        fields = ["id", "department", "position", "employment_status", "contract_type", "start_date", "end_date", "note"]
