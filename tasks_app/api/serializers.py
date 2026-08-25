from rest_framework import serializers
from django.contrib.auth import get_user_model
from ..models import Task
from auth_app.api.serializers import UserProfileSerializer

User = get_user_model()

class TaskDetailSerializer(serializers.ModelSerializer):
  """
  Serializer for retrieving task details.

  Includes nested user profiles for the assignee and reviewer and a read-only field for the
  total comments count.
  """
  assignee = UserProfileSerializer(read_only=True, allow_null=True)
  reviewer = UserProfileSerializer(read_only=True, allow_null=True)
  comments_count = serializers.ReadOnlyField(source="annotated_comments_count")

  class Meta:
    model = Task
    fields = ["id", "board", "title", "description", "status", "priority", "assignee", "reviewer", "due_date", "comments_count"]


class TaskCreateAndUpdateSerializer(serializers.ModelSerializer):
  """Serializer for creating and updating a task."""
  assignee_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source="assignee", required=False, allow_null=True)
  reviewer_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source="reviewer", required=False, allow_null=True)

  class Meta:
    model = Task
    fields = ["board", "title", "description", "status", "priority", "assignee_id", "reviewer_id", "due_date"]

  def validate_board(self, value):
    """Ensures that the board cannot be changed while updating a task."""
    if self.instance and self.instance.board != value:
      raise serializers.ValidationError("The board for this task cannot be changed.")
    return value



