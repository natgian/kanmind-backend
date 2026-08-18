from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers

User = get_user_model()

class RegistrationSerializer(serializers.ModelSerializer):
  """Validate and create a new user."""
  repeated_password = serializers.CharField(write_only=True)

  class Meta:
    model = User
    fields = ["fullname", "email", "password", "repeated_password"]
    extra_kwargs = {"password": {"write_only": True}}

  def validate(self, data):
    """Check that the two password fields match."""
    if data["password"] != data["repeated_password"]:
      raise serializers.ValidationError({"password": "Passwords do not match."})
    return data

  def create(self, validated_data):
    """Create and return a new user with email as username."""
    validated_data.pop("repeated_password")
    user = User.objects.create_user(**validated_data)
    return user


class LoginSerializer(serializers.Serializer):
  """Validate and log in user."""
  email = serializers.EmailField()
  password = serializers.CharField(write_only=True, style={"input_type": "password"})

  def validate(self, data):
    """Validate credentials and authenticate the user."""
    email = data.get("email")
    password = data.get("password")

    if email and password:
      user = authenticate(request=self.context.get("request"), username=email, password=password)

      if not user:
        raise serializers.ValidationError("Invalid email or password.")

      data["user"] = user
    else:
      raise serializers.ValidationError("Both email and password are required.")

    return data


  class UserProfileSerializer(serializers.ModelSerializer):
    """Display user information."""
    class Meta:
      model = User
      fields = ["id", "email", "fullname"]
  