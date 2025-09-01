from django.contrib.auth.models import User
from rest_framework import viewsets, status, generics, mixins
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from .serializers import RegistrationSerializer

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