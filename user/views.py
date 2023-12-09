from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication

from .serializers import UserSerializer


class CreateUserView(generics.CreateAPIView):
    """Create and save user in Database User table"""
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)


class ManagerUserView(generics.RetrieveUpdateAPIView):
    """Return current user and authentication is required"""
    serializer_class = UserSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user
