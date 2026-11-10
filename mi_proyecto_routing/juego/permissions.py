from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    message = 'Acceso prohibido. Se requiere rol ADMIN.'


    def has_permission(self, request, view):

        if not request.user or not request.user.is_authenticated:

            return False

        return hasattr(request.user, 'profile') and request.user.profile.role == 'ADMIN'