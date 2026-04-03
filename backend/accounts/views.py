from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
import pyotp
import secrets

from .serializers import (
    RegisterSerializer, UserSerializer,
    CustomTokenObtainPairSerializer,
    TwoFASetupSerializer, TwoFAConfirmSerializer, TwoFADisableSerializer,
    BackupCodesSerializer, generate_backup_codes
)
from audit.models import AuditLog

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = RegisterSerializer

class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, *args, **kwargs):
        return Response(UserSerializer(request.user).data)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        ip = request.META.get("REMOTE_ADDR")
        ua = request.META.get("HTTP_USER_AGENT")
        email = request.data.get("email") or request.data.get("username") or ""
        try:
            serializer.is_valid(raise_exception=True)
            user = getattr(serializer, "user", None)
            if user:
                AuditLog.objects.create(
                    actor=user,
                    action="LOGIN",
                    model="User",
                    object_id=str(user.pk),
                    changes={"ip": ip, "user_agent": ua},
                )
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        except Exception:
            AuditLog.objects.create(
                actor=None,
                action="LOGIN_FAILED",
                model="User",
                object_id=email or "unknown",
                changes={"ip": ip, "user_agent": ua},
            )
            raise

class CustomTokenRefreshView(TokenRefreshView):
    pass

class TwoFASetupView(APIView):
    """
    POST to initialize/re-initialize 2FA setup.
    Returns the OTPAuth URI for QR code generation.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        
        # Generate new secret (or regenerate if already exists)
        user.twofa_secret = pyotp.random_base32()
        user.save(update_fields=["twofa_secret"])
        
        issuer = "HRIS"
        label = f"{issuer}:{user.email}"
        uri = pyotp.totp.TOTP(user.twofa_secret).provisioning_uri(
            name=label, 
            issuer_name=issuer
        )
        
        AuditLog.objects.create(
            actor=user,
            action="UPDATE",
            model="User",
            object_id=str(user.pk),
            changes={"info": "2FA setup initialized"}
        )
        
        return Response(
            TwoFASetupSerializer({"otpauth_uri": uri}).data,
            status=status.HTTP_200_OK
        )

class TwoFAConfirmEnableView(APIView):
    """
    POST to confirm and enable 2FA after setup.
    Requires valid OTP to verify the user has configured their authenticator.
    Returns backup codes.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        ser = TwoFAConfirmSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        
        otp = ser.validated_data["otp"]
        
        if not user.twofa_secret:
            return Response(
                {"detail": "2FA not initialized. Call setup first."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        totp = pyotp.TOTP(user.twofa_secret)
        if not totp.verify(otp, valid_window=1):
            return Response(
                {"detail": "Invalid OTP."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Enable 2FA and generate backup codes
        user.twofa_enabled = True
        codes, hashes = generate_backup_codes()
        user.backup_codes = hashes
        user.save(update_fields=["twofa_enabled", "backup_codes"])
        
        AuditLog.objects.create(
            actor=user,
            action="UPDATE",
            model="User",
            object_id=str(user.pk),
            changes={"info": "2FA enabled"}
        )

        return Response(
            BackupCodesSerializer({"codes": codes}).data,
            status=status.HTTP_200_OK
        )

class TwoFADisableView(APIView):
    """
    POST to disable 2FA.
    Requires either valid OTP or backup code for security.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        ser = TwoFADisableSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        
        otp = ser.validated_data.get("otp") or ""
        backup_code = ser.validated_data.get("backup_code") or ""

        if user.twofa_enabled:
            if otp:
                # Verify OTP
                totp = pyotp.TOTP(user.twofa_secret or "")
                if not totp.verify(otp, valid_window=1):
                    return Response(
                        {"detail": "Invalid OTP."}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
            elif backup_code:
                # Verify backup code
                from django.contrib.auth.hashers import check_password
                hashes = list(user.backup_codes or [])
                ok = False
                for i, h in enumerate(hashes):
                    if check_password(backup_code, h):
                        hashes.pop(i)
                        ok = True
                        break
                if not ok:
                    return Response(
                        {"detail": "Invalid backup code."}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                user.backup_codes = hashes
            else:
                return Response(
                    {"detail": "OTP or backup code required."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Disable 2FA and clear secrets
        user.twofa_enabled = False
        user.twofa_secret = None
        user.backup_codes = []
        user.save(update_fields=["twofa_enabled", "twofa_secret", "backup_codes"])
        
        AuditLog.objects.create(
            actor=user,
            action="UPDATE",
            model="User",
            object_id=str(user.pk),
            changes={"info": "2FA disabled"}
        )

        return Response(
            {"detail": "2FA disabled successfully."},
            status=status.HTTP_200_OK
        )


class PasswordResetRequestView(APIView):
    """
    POST {email} — generates a reset token, emails it to the user.
    Always returns 200 to avoid leaking whether an email exists.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        from .serializers import PasswordResetRequestSerializer
        from notifications.utils import send_email_message
        from django.conf import settings as conf
        import hashlib

        ser = PasswordResetRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        email = ser.validated_data["email"]

        user = User.objects.filter(email__iexact=email, is_active=True).first()
        if user:
            raw_token = secrets.token_urlsafe(48)
            token_hash = hashlib.sha256(raw_token.encode()).hexdigest()

            # Store token hash + expiry on user (reuse locked_until idea, but separate field)
            from django.core.cache import cache
            cache.set(f"pwd_reset_{token_hash}", user.pk, timeout=3600)  # 1 hour

            frontend_url = getattr(conf, "FRONTEND_BASE_URL", "http://localhost:5173")
            reset_link = f"{frontend_url}/login?reset_token={raw_token}"

            send_email_message(
                user.email,
                subject="HRIS Password Reset",
                body=(
                    f"Hello {user.full_name},\n\n"
                    f"Click the link below to reset your password:\n{reset_link}\n\n"
                    f"This link expires in 1 hour.\n\n"
                    f"If you did not request this, please ignore this email."
                ),
            )

            AuditLog.objects.create(
                actor=None,
                action="UPDATE",
                model="User",
                object_id=str(user.pk),
                changes={"info": "Password reset requested"},
            )

        return Response({"detail": "If the email exists, a reset link has been sent."})


class PasswordResetConfirmView(APIView):
    """
    POST {token, new_password} — validates token and resets password.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        from .serializers import PasswordResetConfirmSerializer
        from django.core.cache import cache
        import hashlib

        ser = PasswordResetConfirmSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        raw_token = ser.validated_data["token"]
        new_password = ser.validated_data["new_password"]
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()

        user_pk = cache.get(f"pwd_reset_{token_hash}")
        if not user_pk:
            return Response(
                {"detail": "Invalid or expired reset token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.filter(pk=user_pk, is_active=True).first()
        if not user:
            return Response(
                {"detail": "Invalid or expired reset token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.save(update_fields=["password"])
        cache.delete(f"pwd_reset_{token_hash}")

        AuditLog.objects.create(
            actor=user,
            action="UPDATE",
            model="User",
            object_id=str(user.pk),
            changes={"info": "Password reset completed"},
        )

        return Response({"detail": "Password has been reset successfully."})