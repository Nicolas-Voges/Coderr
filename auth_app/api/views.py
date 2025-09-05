from django.contrib.auth.models import User
from rest_framework import viewsets, status, generics, mixins
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from .serializers import RegistrationSerializer, ProfileSerializer
from auth_app.models import Profile

class RegistrationView(generics.CreateAPIView):



    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = [RegistrationSerializer]

    def post(self, request):
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
    permission_classes = [AllowAny]
    queryset = User.objects.all()

    def post(self, request):
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
    permission_classes = [IsAuthenticated] # IsOwner
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()
