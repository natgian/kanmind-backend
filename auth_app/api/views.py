from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .serializers import RegistrationSerializer, LoginSerializer

class RegistrationView(GenericAPIView):
  """API endpoint for creating a new user and returning a token."""
  permission_classes = [AllowAny]
  serializer_class = RegistrationSerializer

  def post(self, request):
    """Handle POST request to create a user."""
    serializer = self.get_serializer(data=request.data)

    if serializer.is_valid():
      user = serializer.save()
      # Generate token for the new user
      token, created = Token.objects.get_or_create(user=user)

      response_data = {
        "token":token.key,
        "fullname": user.fullname,
        "email": user.email,
        "user_id": user.id
      }
      return Response(response_data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(GenericAPIView):
  """API endpoint for user login."""
  permission_classes = [AllowAny]
  serializer_class = LoginSerializer

  def post(self, request, *args, **kwargs):
    """Validate credentials and return an authentication token with user details."""
    serializer = self.get_serializer(data=request.data, context={"request": request})

    if serializer.is_valid():
      user = serializer.validated_data["user"]
      token, created = Token.objects.get_or_create(user=user)

      response_data = {
        "token": token.key,
        "fullname": user.fullname,
        "email": user.email,
        "user_id": user.id
      }
      return Response(response_data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)