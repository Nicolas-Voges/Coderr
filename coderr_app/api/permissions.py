from rest_framework.permissions import BasePermission

class IsTypeBusiness(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.user

class IsSuperUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_superuser