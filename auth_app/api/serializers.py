from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()

class RegistrationSerializer(serializers.ModelSerializer):
  """Validates and creates a new user."""

  repeated_password = serializers.CharField(write_only=True)

  class Meta:
    model = User
    fields = ["fullname", "email", "password", "repeated_password"]
    extra_kwargs = {"password": {"write_only": True}}

  def validate(self, data):
    """
    Checks that the two password fields match.
    """

    if data["password"] != data["repeated_password"]:
      raise serializers.ValidationError({"password:" "Passwords do not match."})
    return data

  def create(self, validated_data):
    """
    Creates amd returns a new User with email as username.
    """

    validated_data.pop("repeated_password")

    user = User.objects.create_user(
      username=validated_data["email"],
      email=validated_data["email"],
      fullname=validated_data["fullname"],
      password=validated_data["password"]
    )
    return user

  