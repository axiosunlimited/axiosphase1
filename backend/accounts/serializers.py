from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.signals import user_login_failed
import pyotp
import secrets
from datetime import timedelta

User = get_user_model()

LOCKOUT_THRESHOLD = 5
LOCKOUT_MINUTES = 10

class UserSerializer(serializers.ModelSerializer):
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "role", "twofa_enabled", "permissions"]

    def get_permissions(self, obj):
        return sorted(obj.get_all_permissions())

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "role", "password"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User.objects.create_user(password=password, **validated_data)
        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    otp = serializers.CharField(required=False, allow_blank=True)
    backup_code = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user

        # lockout check
        if user.locked_until and user.locked_until > timezone.now():
            raise serializers.ValidationError({"detail": "Account temporarily locked. Try again later."})

        otp = attrs.get("otp") or ""
        backup_code = attrs.get("backup_code") or ""

        if user.twofa_enabled:
            if otp:
                totp = pyotp.TOTP(user.twofa_secret or "")
                if not totp.verify(otp, valid_window=1):
                    self._fail_login(user)
                    user_login_failed.send(sender=self.__class__, credentials={"email": user.email}, request=self.context.get("request"))
                    raise serializers.ValidationError({"detail": "Invalid OTP code."})
            elif backup_code:
                if not self._consume_backup_code(user, backup_code):
                    self._fail_login(user)
                    user_login_failed.send(sender=self.__class__, credentials={"email": user.email}, request=self.context.get("request"))
                    raise serializers.ValidationError({"detail": "Invalid backup code."})
            else:
                user_login_failed.send(sender=self.__class__, credentials={"email": user.email}, request=self.context.get("request"))
                raise serializers.ValidationError({"detail": "OTP or backup code required."})

        # success -> reset counters
        user.failed_login_attempts = 0
        user.locked_until = None
        user.save(update_fields=["failed_login_attempts", "locked_until"])
        return data

    def _fail_login(self, user):
        user.failed_login_attempts += 1
        if user.failed_login_attempts >= LOCKOUT_THRESHOLD:
            user.locked_until = timezone.now() + timedelta(minutes=LOCKOUT_MINUTES)
        user.save(update_fields=["failed_login_attempts", "locked_until"])

    def _consume_backup_code(self, user, code):
        hashes = list(user.backup_codes or [])
        for i, h in enumerate(hashes):
            if check_password(code, h):
                hashes.pop(i)
                user.backup_codes = hashes
                user.save(update_fields=["backup_codes"])
                return True
        return False

class TwoFASetupSerializer(serializers.Serializer):
    otpauth_uri = serializers.CharField(read_only=True)

class TwoFAConfirmSerializer(serializers.Serializer):
    otp = serializers.CharField()

class TwoFADisableSerializer(serializers.Serializer):
    otp = serializers.CharField(required=False, allow_blank=True)
    backup_code = serializers.CharField(required=False, allow_blank=True)

class BackupCodesSerializer(serializers.Serializer):
    codes = serializers.ListField(child=serializers.CharField(), read_only=True)

def generate_backup_codes(n=10):
    codes = []
    hashes = []
    for _ in range(n):
        code = secrets.token_hex(4)  # 8 hex chars
        codes.append(code)
        hashes.append(make_password(code))
    return codes, hashes


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField(min_length=8)
