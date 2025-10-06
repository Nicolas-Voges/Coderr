"""
Django REST Framework views for authentication and user profiles.

This module provides views for registration, login, profile retrieval,
updates, and listing users by type (customer/business).
"""

from django.contrib.auth.models import User

from rest_framework import status, generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response

from auth_app.models import Profile
from .serializers import RegistrationSerializer, ProfileSerializer
from .permissions import IsOwner

class RegistrationView(generics.CreateAPIView):
    """
    Handle user registration and token creation.
    """
    
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = [RegistrationSerializer]

    def post(self, request):
        """
        Register a new user and return authentication token.

        Returns
        -------
        Response
            JSON with token, username, email, and user ID.
        """

        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            saved_account = serializer.save()
            token, created = Token.objects.get_or_create(user=saved_account)
            data = {
                'token': token.key,
                'username': saved_account.username,
                'email': saved_account.email,
                'user_id': saved_account.id
            }
            return Response(data, status=status.HTTP_201_CREATED)
        else:
            data=serializer.errors
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        

class LoginView(ObtainAuthToken):
    """
    Handle user login and return authentication token.
    """

    permission_classes = [AllowAny]
    queryset = User.objects.all()

    def post(self, request):
        """
        Authenticate user and return token with basic user info.

        Returns
        -------
        Response
            JSON with token, username, email, and user ID.
        """

        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            user =serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            data = {
                'token': token.key,
                'username': user.username,
                'email': user.email,
                'user_id': user.id
            }
            return Response(data, status=status.HTTP_200_OK)
        else:
            data = serializer.errors
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        

class ProfileUpdateRetriveView(generics.RetrieveUpdateAPIView):
    """
    Retrieve or update the authenticated user's profile.
    """
    permission_classes = [IsAuthenticated, IsOwner]
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()


class ProfileListView(generics.ListAPIView):
    """
    List all profiles or filter them by type (business/customer).
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()

    def get_queryset(self):
        """Return filtered queryset based on path ('business' or 'customer')."""
        queryset = super().get_queryset()
        path = self.request.path

        if "business" in path:
            return queryset.filter(type="business")
        elif "customer" in path:
            return queryset.filter(type="customer")
        return queryset