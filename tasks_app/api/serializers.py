from rest_framework import serializers
from django.contrib.auth import get_user_model
from ..models import Task
from auth_app.api.serializers import UserProfileSerializer

User = get_user_model()

class TaskSerializer(serializers.ModelSerializer):
  """
  Serializer for retrieving task details.

  Includes nested user profiles for the assignee and reviewer and a read-only field for the
  total comment count.
  """
  assignee = UserProfileSerializer(read_only=True, allow_null=True)
  reviewer = UserProfileSerializer(read_only=True, allow_null=True)
  comments_count = serializers.ReadOnlyField(source="annotated_comments_count")

  class Meta:
    model = Task
    fields = ["id", "title", "description", "status", "priority", "assignee", "reviewer", "due_date", "comments_count"]