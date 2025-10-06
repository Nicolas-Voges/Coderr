"""
Custom permission classes for authentication app.
"""

from rest_framework.permissions import BasePermission

class IsOwner(BasePermission):
    """
    Allow updates only if the authenticated user owns the object.
    """

    def has_object_permission(self, request, view, obj):
        """
        Check object-level permissions.

        Returns True if the request is a PATCH and the requesting user
        is the owner of the object. Falls back to default otherwise.
        """
        
        if request.method == 'PATCH':
            return request.user == obj.user
        return super().has_object_permission(request, view, obj)