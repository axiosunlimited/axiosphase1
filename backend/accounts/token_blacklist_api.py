from django.contrib.auth import get_user_model
from rest_framework import viewsets, permissions, decorators, status, mixins
from rest_framework.response import Response
from rest_framework import serializers

from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken

from audit.mixins import AuditMixin
from accounts.permissions import RolePermission
from accounts.models import User

UserModel = get_user_model()


class OutstandingTokenSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = OutstandingToken
        fields = [
            "id",
            "user",
            "user_email",
            "jti",
            "token",
            "created_at",
            "expires_at",
        ]
        read_only_fields = fields


class BlacklistedTokenSerializer(serializers.ModelSerializer):
    token_id = serializers.IntegerField(source="token.id", read_only=True)
    user_email = serializers.CharField(source="token.user.email", read_only=True)
    jti = serializers.CharField(source="token.jti", read_only=True)
    expires_at = serializers.DateTimeField(source="token.expires_at", read_only=True)

    class Meta:
        model = BlacklistedToken
        fields = ["id", "token", "token_id", "user_email", "jti", "blacklisted_at", "expires_at"]
        read_only_fields = fields


class OutstandingTokenViewSet(AuditMixin, viewsets.ReadOnlyModelViewSet):
    queryset = OutstandingToken.objects.select_related("user").all().order_by("-created_at")
    serializer_class = OutstandingTokenSerializer
    allowed_roles = [User.Role.SYSTEM_ADMIN]
    permission_classes = [permissions.IsAuthenticated, RolePermission]

    @decorators.action(detail=True, methods=["post"])
    def blacklist(self, request, *args, **kwargs):
        tok = self.get_object()
        BlacklistedToken.objects.get_or_create(token=tok)
        self.audit_log("DELETE", tok, {"info": "Token manually blacklisted"})
        return Response({"detail": "Token blacklisted."})


class BlacklistedTokenViewSet(AuditMixin, mixins.DestroyModelMixin, viewsets.ReadOnlyModelViewSet):
    queryset = BlacklistedToken.objects.select_related("token", "token__user").all().order_by("-blacklisted_at")
    serializer_class = BlacklistedTokenSerializer
    allowed_roles = [User.Role.SYSTEM_ADMIN]
    permission_classes = [permissions.IsAuthenticated, RolePermission]

    def destroy(self, request, *args, **kwargs):
        # allow un-blacklisting by deleting record
        if request.user.role not in [User.Role.SYSTEM_ADMIN]:
            return Response({"detail": "Not allowed."}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)