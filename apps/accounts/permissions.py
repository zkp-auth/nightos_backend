from rest_framework.permissions import BasePermission

class IsAdminUserRole(BasePermission):
    """
    Allows access only to users with the "admin" role.
    """

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == "admin"
        )

class IsAdminOrManager(BasePermission):
    """
    Allows access to authenticate users with "admin" or "manager" role.
    """

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in ["admin", "manager"]
        )
