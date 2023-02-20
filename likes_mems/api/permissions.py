from rest_framework.permissions import BasePermission


class PremiumUserOrAdmin(BasePermission):

    def has_permission(self, request, view):

        return request.user.is_authenticated and (
            request.user.is_superuser or request.user.is_premium
        )

    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and (
            request.user.is_superuser or request.user.is_premium
        )
