from django.urls import path
from .views import (
    RegisterView, MeView,
    CustomTokenObtainPairView, CustomTokenRefreshView,
    TwoFASetupView, TwoFAConfirmEnableView, TwoFADisableView,
    PasswordResetRequestView, PasswordResetConfirmView,
)
from .invite_views import (
    InvitesListCreateView,
    InviteCreateAliasView,
    InviteResendView,
    InviteValidateView,
    AcceptInviteView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("me/", MeView.as_view(), name="me"),

    path("token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),

    path("2fa/setup/", TwoFASetupView.as_view(), name="2fa_setup"),
    path("2fa/enable/", TwoFAConfirmEnableView.as_view(), name="2fa_enable"),
    path("2fa/disable/", TwoFADisableView.as_view(), name="2fa_disable"),

    # Invite-based onboarding
    path("invites/", InvitesListCreateView.as_view(), name="invites_list_create"),
    path("invites/<int:invite_id>/resend/", InviteResendView.as_view(), name="invite_resend"),
    path("invites/validate/", InviteValidateView.as_view(), name="invite_validate"),

    # Password reset
    path("password-reset/", PasswordResetRequestView.as_view(), name="password_reset_request"),
    path("password-reset/confirm/", PasswordResetConfirmView.as_view(), name="password_reset_confirm"),

    # Aliases requested
    path("invite/", InviteCreateAliasView.as_view(), name="invite_create"),
    path("accept-invite/", AcceptInviteView.as_view(), name="accept_invite"),
]
