from rest_framework import permissions


def user_company_ids(user):
    return list(
        user.company_memberships.values_list("company_id", flat=True).distinct()
    )


def is_app_admin(user) -> bool:
    """LabourPro App Admin = Django superuser (sole whole-app admin)."""
    return bool(
        user
        and getattr(user, "is_authenticated", False)
        and getattr(user, "is_superuser", False)
        and getattr(user, "is_active", False)
    )


class IsAuthenticatedCompanyMember(permissions.BasePermission):
    """User must belong to at least one company (membership)."""

    message = "No company membership for this user."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if not request.user.is_active:
            return False
        return bool(user_company_ids(request.user))


class IsAppAdmin(permissions.BasePermission):
    """Only the whole-app Admin (superuser) may access /api/admin/*."""

    message = "App admin access required."

    def has_permission(self, request, view):
        return is_app_admin(request.user)
