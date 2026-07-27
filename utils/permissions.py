from rest_framework import permissions


class AuthenticatedUserPermission(permissions.BasePermission):
    message = 'Unauthorised User Not Allowed.'

    def has_permission(self, request, view):
        if 'Authorization' not in request.headers.keys():
            return False
        headers = {
            'Authorization': request.headers.get('Authorization')
        }

        # check roles
        
        return super().has_permission(request, view)
