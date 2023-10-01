from rest_framework.permissions import BasePermission


class StaffOnly(BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated and request.user.is_staff)