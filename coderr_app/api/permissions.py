from rest_framework.exceptions import NotFound
from rest_framework.permissions import BasePermission
from auth_app.models import Profile
from coderr_app.models import Detail

class IsTypeBusiness(BasePermission):
    def has_permission(self, request, view):
        user_type = Profile.objects.get(user=request.user).type
        return user_type == 'business'
    

class IsTypeCustomerAndForced404(BasePermission):
    def has_permission(self, request, view):
        id = request.data.get('offer_detail_id')
        if isinstance(id, int) and id > 0:
            try:
                Detail.objects.get(id=request.data['offer_detail_id'])
            except Detail.DoesNotExist:
                raise NotFound
        user_type = Profile.objects.get(user=request.user).type
        return user_type == 'customer'
    

class IsTypeCustomer(BasePermission):
    def has_permission(self, request, view):
        user_type = Profile.objects.get(user=request.user).type
        return user_type == 'customer'


class IsSuperOrStaffUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_superuser or request.user.is_staff
    
    
class IsOfferOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.user
    

class IsOrderOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.business_user
    

class IsReviewOwnerAndForced404(BasePermission):
    def has_object_permission(self, request, view, obj):
        pk = view.kwargs.get('pk')
        if isinstance(id, int) and id > 0:
            try:
                Detail.objects.get(id=pk)
            except Detail.DoesNotExist:
                raise NotFound
        return request.user == obj.reviewer