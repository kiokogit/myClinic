from rest_framework import permissions


class AuthenticatedUserPermission(permissions.BasePermission):
    message = 'You do not have permission to perform this action'

    def has_permission(self, request, view):
        return super().has_permission(request, view)

class PublicUserPermissionsOnly(AuthenticatedUserPermission):

    def has_permission(self, request, view):
        if request.user.user_type != 'public':
            return False
        return super().has_permission(request, view)

class DoctorPermissionOnly(AuthenticatedUserPermission):

    def has_permission(self, request, view):
            if request.user.user_type != 'doctor':
                return False
            return super().has_permission(request, view)
    

