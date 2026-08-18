from rest_framework import serializers
from django.contrib.auth import get_user_model
from ..models import Board

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


  