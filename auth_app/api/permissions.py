from django.contrib.auth.models import User
from rest_framework.permissions import BasePermission
from rest_framework.generics import get_object_or_404
from rest_framework.exceptions import NotFound

class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method == 'PATCH':
            return request.user == obj.user
        return super().has_object_permission(request, view, obj)