from rest_framework import serializers
from django.contrib.auth import get_user_model
from models import Board

User = get_user_model()

class BoardSerializer(serializers.ModelSerializer):
  """
  Serializer for creating and retrieving a board.

  Validates incoming member IDs and dynamically computes fields for tasks and member count.
  """
  members = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all(), required=False)
  owner_id = serializers.ReadOnlyField(source="owner.id")
  member_count = serializers.SerializerMethodField()
  ticket_count = serializers.SerializerMethodField()
  tasks_to_do_count = serializers.SerializerMethodField()
  tasks_high_prio_count = serializers.SerializerMethodField()

  class Meta:
    model = Board
    fields = ["id", "title", "member_count", "ticket_count", "tasks_to_do_count", "tasks_high_prio_count", "owner_id"]

  def get_member_count(self, obj):
    """Return the total number of members assigned to the board."""
    return obj.members.count()

  def get_ticket_count(self, obj):
    """Return the total number ot tasks (tickets) associated to the board."""
    return obj.tasks.count()

  def get_tasks_to_do_count(self, obj):
    """Return the total number of tasks (tickets) associated to the board with the status 'to-do'."""
    return obj.tasks.filter(status="to-do").count()

  def get_tasks_high_prio_count(self, obj):
    """Return the total number ot tasks (tickets) associated to the board with the priority 'high'."""
    return obj.tasks.filter(priority="high").count()

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


  