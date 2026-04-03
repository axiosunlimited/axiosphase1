from rest_framework.permissions import BasePermission, SAFE_METHODS

def has_role(user, roles):
    return getattr(user, "role", None) in roles

class RolePermission(BasePermission):
    """Allow access if the authenticated user role is in view.allowed_roles."""
    def has_permission(self, request, view):
        roles = getattr(view, "allowed_roles", None)
        if roles is None:
            return True
        return bool(request.user and request.user.is_authenticated and has_role(request.user, roles))
