from rest_framework.permissions import BasePermission
from auth_app.models import Profile

class IsTypeBusiness(BasePermission):
    def has_permission(self, request, view):
        user_type = Profile.objects.get(user=request.user).type
        return user_type == 'business'
    

class IsTypeCustomer(BasePermission):
    def has_permission(self, request, view):
        user_type = Profile.objects.get(user=request.user).type
        return user_type == 'customer'


class IsSuperUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_superuser
    

class IsStaffUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_staff
    

class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.user or request.user == obj.business_user