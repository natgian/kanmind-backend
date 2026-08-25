from rest_framework import permissions
from django.shortcuts import get_object_or_404
from boards_app.models import Board

class IsBoardMember(permissions.BasePermission):
  """
  Allows access for GET and PATCH requests only if the user is a member of the board.

  - On POST: checks if the user is a member of the sent board 
  - On GET/PATCH/DELETE: checks if the user is a member in the board from the task
  """
  def has_permission(self, request, view):
    """
    On POST request check if the user is a member of the board with the sent board ID.
    Raises 404 if board doesn't exist, otherwise returns True if the user is a member.
    """
    if request.method == "POST":
      board_id = request.data.get("board")
      if not board_id:
        return True
      board = get_object_or_404(Board, id=board_id)
      return board.members.filter(id=request.user.id).exists()
    return True

  def has_object_permission(self, request, view, obj):
    """On GET/PATCH/DELETE request check if the user is a member of the board in the current task."""
    is_member = obj.board.members.filter(id=request.user.id).exists()
    return is_member