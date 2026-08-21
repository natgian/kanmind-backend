from rest_framework import serializers
from django.contrib.auth import get_user_model
from ..models import Board
from auth_app.api.serializers import UserProfileSerializer
from tasks_app.api.serializers import TaskDetailSerializer

User = get_user_model()

class BoardSerializer(serializers.ModelSerializer):
  """
  Serializer for creating a board and listing boards.

  Validates incoming member IDs and maps annotated statistics (like member and task counts) from the database view.
  """
  members = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all(), required=False, write_only=True)
  owner_id = serializers.ReadOnlyField(source="owner.id")

  member_count = serializers.ReadOnlyField(source="annotated_member_count")
  ticket_count = serializers.ReadOnlyField(source="annotated_ticket_count")
  tasks_to_do_count = serializers.ReadOnlyField(source="annotated_tasks_to_do_count")
  tasks_high_prio_count = serializers.ReadOnlyField(source="annotated_tasks_high_prio_count")

  class Meta:
    model = Board
    fields = ["id", "title", "members", "member_count", "ticket_count", "tasks_to_do_count", "tasks_high_prio_count", "owner_id"]

  def create(self, validated_data):
    """Create a new board and automatically assign the creator as the owner and as a member of the board."""
    request = self.context.get("request")

    if request is None:
      raise serializers.ValidationError("HTTP-Request context is missing.")

    current_user = request.user
    members_data = validated_data.pop("members", [])

    # Ensure that the creator is always included in the members list
    if current_user not in members_data:
      members_data.append(current_user)

    board = Board.objects.create(owner=current_user, **validated_data)
    board.members.set(members_data)

    return board


class BoardDetailSerializer(serializers.ModelSerializer):
  """
  Serializer for retrieving detailed information of a single board.

  Includes nested representations of assigned board members and associated tasks (with calculated)
  comment counts).
  """
  owner_id = serializers.ReadOnlyField(source="owner.id")
  members = UserProfileSerializer(many=True, read_only=True)
  tasks = TaskDetailSerializer(many=True, read_only=True)
    
  class Meta:
    model = Board
    fields = ["id", "title", "owner_id", "members", "tasks"]


class BoardUpdateSerializer(serializers.ModelSerializer):
  """
  Serializer for updating a board.

  Accepts a list of user IDs for input ('members') and returns fully nested user information ('members_data', 'owner_data') in the response.
  """
  members = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all(), write_only=True)
  members_data = UserProfileSerializer(source="members", many=True, read_only=True)
  owner_data = UserProfileSerializer(source="owner", read_only=True)  

  class Meta:
    model = Board
    fields = ["id", "title", "owner_data", "members_data", "members"]


class EmailCheckSerializer(serializers.Serializer):
  """Serializer for checking if email is already registered to a user."""
  email = serializers.EmailField(required=True)

  