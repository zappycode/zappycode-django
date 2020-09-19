from rest_framework import permissions


class IsMember(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.active_membership:
            return True
        return False
