from rest_framework import permissions


def user_company_ids(user):
    return list(
        user.company_memberships.values_list("company_id", flat=True).distinct()
    )


class IsAuthenticatedCompanyMember(permissions.BasePermission):
    """User must belong to at least one company (membership)."""

    message = "No company membership for this user."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return user_company_ids(request.user)
