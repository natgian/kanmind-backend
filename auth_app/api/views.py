from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token

from .serializers import RegistrationSerializer

class RegistrationView(APIView):
  """API endpoint for creating a new user and returning a token."""
  permission_classes = [AllowAny]

  def post(self, request):
    """Handle POST request to create a user."""
    serializer = RegistrationSerializer(data=request.data)

    if serializer.is_valid():
      user = serializer.save()

      # Generate token for the new user
      token, created = Token.objects.get_or_create(user=user)

      # Structure response data
      response_data = {
        "token":token.key,
        "fullname": user.fullname,
        "email": user.email,
        "user_id": user.id
      }
      return Response(response_data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

