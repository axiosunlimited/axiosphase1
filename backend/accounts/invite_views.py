import hashlib
import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from audit.models import AuditLog
from accounts.permissions import RolePermission
from .models import UserInvite
from .utils import create_and_send_invite, _hash_token, _build_activation_link
from .invite_serializers import (
    InviteCreateSerializer,
    InviteSerializer,
    InviteValidateResponseSerializer,
    InviteAcceptSerializer,
)


User = get_user_model()


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _build_activation_link(token: str) -> str:
    base = getattr(settings, "FRONTEND_BASE_URL", "").rstrip("/")
    path = getattr(settings, "INVITE_ACCEPT_PATH", "/accept-invite")
    if not path.startswith("/"):
        path = "/" + path
    return f"{base}{path}?token={token}" if base else f"{path}?token={token}"


class InvitesListCreateView(generics.ListAPIView):
    """Admin/HR endpoint: list invites (GET) and create invites (POST)."""

    serializer_class = InviteSerializer
    allowed_roles = [User.Role.SYSTEM_ADMIN, User.Role.HR_MANAGER, User.Role.HR_OFFICER]
    permission_classes = [permissions.IsAuthenticated, RolePermission]

    def get_queryset(self):
        qs = UserInvite.objects.select_related("user", "created_by").all()
        status_filter = (self.request.query_params.get("status") or "").lower().strip()
        email_filter = (self.request.query_params.get("email") or "").strip()
        now = timezone.now()

        if email_filter:
            qs = qs.filter(email__icontains=email_filter)

        if status_filter in {"pending", "used", "expired"}:
            if status_filter == "used":
                qs = qs.filter(used_at__isnull=False)
            elif status_filter == "expired":
                qs = qs.filter(used_at__isnull=True, expires_at__lte=now)
            elif status_filter == "pending":
                qs = qs.filter(used_at__isnull=True, expires_at__gt=now)

        return qs

    def post(self, request, *args, **kwargs):
        ser = InviteCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data

        email = data["email"].lower().strip()
        first_name = data.get("first_name", "")
        last_name = data.get("last_name", "")
        role = data.get("role") or User.Role.EMPLOYEE
        auto_activate = bool(data.get("auto_activate", False))

        expires_in_days = data.get("expires_in_days")
        default_days = getattr(settings, "INVITE_EXPIRE_DAYS", 7)
        days = int(expires_in_days or default_days)

        # Create or reuse a user
        user = User.objects.filter(email__iexact=email).first()
        if user:
            # If the user is already active and has a usable password, block re-inviting.
            if user.is_active and user.has_usable_password():
                return Response(
                    {"detail": "User already active."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            user = User.objects.create_user(
                email=email,
                password=None,
                first_name=first_name,
                last_name=last_name,
                role=role,
                is_active=False,
            )

        # Ensure user details/role are set by HR/Admin
        changed = False
        if first_name is not None and user.first_name != first_name:
            user.first_name = first_name
            changed = True
        if last_name is not None and user.last_name != last_name:
            user.last_name = last_name
            changed = True
        if role and user.role != role:
            user.role = role
            changed = True

        # Keep the account inactive until acceptance (+ optional auto_activate)
        if user.is_active:
            user.is_active = False
            changed = True

        if changed:
            user.save(update_fields=["first_name", "last_name", "role", "is_active"])

        res = create_and_send_invite(
            user=user,
            creator=request.user,
            expires_in_days=days,
            auto_activate=auto_activate
        )
        invite = res["invite"]
        activation_link = res["activation_link"]
        email_sent = res["email_sent"]
        email_error = res["email_error"]

        return Response(
            {
                "invite_id": invite.pk,
                "email": email,
                "role": role,
                "auto_activate": auto_activate,
                "expires_at": invite.expires_at,
                "activation_link": activation_link,
                "email_sent": email_sent,
                "email_error": email_error,
            },
            status=status.HTTP_201_CREATED,
        )


class InviteCreateAliasView(InvitesListCreateView):
    """Alias for a simpler path: POST /api/<version>/auth/invite/"""

    def get(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class InviteResendView(APIView):
    """Admin/HR endpoint: rotate token and resend invite email."""

    allowed_roles = [User.Role.SYSTEM_ADMIN, User.Role.HR_MANAGER, User.Role.HR_OFFICER]
    permission_classes = [permissions.IsAuthenticated, RolePermission]

    def post(self, request, invite_id: int, *args, **kwargs):
        invite = UserInvite.objects.select_related("user").filter(pk=invite_id).first()
        if not invite:
            return Response({"detail": "Invite not found."}, status=status.HTTP_404_NOT_FOUND)

        if invite.used_at is not None:
            return Response({"detail": "Invite already used."}, status=status.HTTP_400_BAD_REQUEST)

        res = create_and_send_invite(
            user=invite.user,
            creator=request.user,
            auto_activate=invite.auto_activate
        )
        # Use existing invite object (or we could just use the new one, but let's be consistent)
        # Actually create_and_send_invite creates a NEW invite record.
        # This is fine as it expires the old one anyway.
        invite = res["invite"]

        return Response(
            {
                "invite_id": invite.pk,
                "activation_link": res["activation_link"],
                "expires_at": invite.expires_at,
                "email_sent": res["email_sent"],
                "email_error": res["email_error"],
            },
            status=status.HTTP_200_OK,
        )


class InviteValidateView(APIView):
    """Public endpoint: validate token and show who it's for."""

    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        token = (request.query_params.get("token") or "").strip()
        if not token:
            return Response({"detail": "token is required"}, status=status.HTTP_400_BAD_REQUEST)

        invite = UserInvite.objects.select_related("user").filter(token_hash=_hash_token(token)).first()
        if not invite:
            return Response({"detail": "Invalid token."}, status=status.HTTP_404_NOT_FOUND)
        if invite.used_at is not None:
            return Response({"detail": "Invite already used."}, status=status.HTTP_400_BAD_REQUEST)
        if invite.is_expired:
            return Response({"detail": "Invite expired."}, status=status.HTTP_400_BAD_REQUEST)

        payload = {
            "email": invite.email,
            "full_name": invite.user.full_name,
            "role": invite.role,
            "expires_at": invite.expires_at,
            "auto_activate": invite.auto_activate,
        }
        return Response(InviteValidateResponseSerializer(payload).data, status=status.HTTP_200_OK)


class AcceptInviteView(APIView):
    """Public endpoint: accept invite by setting password."""

    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        ser = InviteAcceptSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        token = ser.validated_data["token"].strip()
        password = ser.validated_data["password"]

        invite = UserInvite.objects.select_related("user").filter(token_hash=_hash_token(token)).first()
        if not invite:
            return Response({"detail": "Invalid token."}, status=status.HTTP_404_NOT_FOUND)
        if invite.used_at is not None:
            return Response({"detail": "Invite already used."}, status=status.HTTP_400_BAD_REQUEST)
        if invite.is_expired:
            return Response({"detail": "Invite expired."}, status=status.HTTP_400_BAD_REQUEST)

        user = invite.user
        user.set_password(password)
        # Ensure role is the one HR/Admin set on the invite
        user.role = invite.role
        if invite.auto_activate:
            user.is_active = True
        user.save(update_fields=["password", "role", "is_active"])

        invite.used_at = timezone.now()
        invite.save(update_fields=["used_at"])

        # Audit: invite accepted
        AuditLog.objects.create(
            actor=user,
            action="UPDATE",
            model="UserInvite",
            object_id=str(invite.pk),
            changes={
                "info": "Invite accepted",
                "auto_activate": invite.auto_activate,
                "activated": bool(user.is_active),
            },
        )
        # Audit: user password set
        AuditLog.objects.create(
            actor=user,
            action="UPDATE",
            model="User",
            object_id=str(user.pk),
            changes={"info": "Password set via invite acceptance"},
        )

        return Response(
            {
                "detail": "Invite accepted.",
                "user_id": user.pk,
                "email": user.email,
                "role": user.role,
                "is_active": user.is_active,
            },
            status=status.HTTP_200_OK,
        )
