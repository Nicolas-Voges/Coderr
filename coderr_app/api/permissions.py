"""
Contains all custom permissions for the Coderr app.

These permissions check:
- User profile type (Business or Customer)
- Ownership of Offers, Orders, and Reviews
- Superuser or Staff rights
- Existence of Offer Details or Reviews (raises 404 if not found)
"""

from rest_framework.exceptions import NotFound
from rest_framework.permissions import BasePermission

from auth_app.models import Profile
from coderr_app.models import Detail, Review

class IsTypeBusiness(BasePermission):
    """Checks if the user has a business profile."""
    def has_permission(self, request, view):
        """Returns True if the user's profile type is business."""
        user_type = Profile.objects.get(user=request.user).type
        return user_type == 'business'
    

class IsTypeBusinessObjPermission(BasePermission):
    """
    Checks if the user has a business profile.
    Raises NotFound if the detail does not exist.
    """
    def has_object_permission(self, request, view, obj):
        """Returns True if the user's profile type is business."""
        user_type = Profile.objects.get(user=request.user).type
        return user_type == 'business'
    

class IsTypeCustomerAndForced404(BasePermission):
    """
    Checks if the user has a Customer profile and the offer detail exists.
    Raises NotFound if the detail does not exist.
    """

    def has_permission(self, request, view):
        """Returns True if the user is a Customer and the offer detail exists."""
        id = request.data.get('offer_detail_id')
        if isinstance(id, int) and id > 0:
            try:
                Detail.objects.get(id=request.data['offer_detail_id'])
            except Detail.DoesNotExist:
                raise NotFound
        user_type = Profile.objects.get(user=request.user).type
        return user_type == 'customer'
    

class IsTypeCustomer(BasePermission):
    """Checks if the user has a Customer profile."""
    def has_permission(self, request, view):
        """Returns True if the user's profile type is 'customer'."""
        user_type = Profile.objects.get(user=request.user).type
        return user_type == 'customer'


class IsSuperOrStaffUser(BasePermission):
    """Checks if the user is a superuser or staff member."""
    def has_permission(self, request, view):
        """Returns True if the user is authenticated and is superuser or staff."""
        return request.user and request.user.is_authenticated and request.user.is_superuser or request.user.is_staff
    
    
class IsOfferOwner(BasePermission):
    """Checks if the user is the owner of the Offer."""
    def has_object_permission(self, request, view, obj):
        """Returns True if the user is the owner of the offer object."""
        return request.user == obj.user
    

class IsOrderOwner(BasePermission):
    """Checks if the user is the owner of the Order."""
    def has_object_permission(self, request, view, obj):
        """Returns True if the user is the business user of the order."""
        return request.user == obj.business_user
    

class IsReviewOwnerAndForced404(BasePermission):
    """Checks if the user is the reviewer of the Review and exists."""
    def has_object_permission(self, request, view, obj):
        """Returns True if the user is the reviewer. Raises NotFound if review ID invalid."""
        pk = view.kwargs.get('pk')
        if isinstance(id, int) and pk > 0:
            try:
                Review.objects.get(id=pk)
            except Review.DoesNotExist:
                raise NotFound
        return request.user == obj.reviewer