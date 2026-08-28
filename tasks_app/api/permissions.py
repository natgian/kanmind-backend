from rest_framework import permissions
from django.shortcuts import get_object_or_404

from boards_app.models import Board
from tasks_app.models import Task

class IsBoardMember(permissions.BasePermission):
  """Allow access only if the user is a board member."""
  def has_permission(self, request, view):
    """Check if the user is a board member."""
    board_id = request.data.get("board")
    task_id = view.kwargs.get("task_id")

    if request.method == "POST" and board_id:
      board = get_object_or_404(Board, id=board_id)
      return board.members.filter(id=request.user.id).exists()
    elif task_id:
      task = get_object_or_404(Task, id=task_id)
      return task.board.members.filter(id=request.user.id).exists()
    return True

  def has_object_permission(self, request, view, obj):
    """
    Check if the user has permission to interact with a task or comment.
    For comments ensure that only the author of the comment can delete it.
    """
    if hasattr(obj, "board"):
      return obj.board.members.filter(id=request.user.id).exists()
    else:
      is_board_member = obj.task.board.members.filter(id=request.user.id).exists()
      if request.method == "DELETE":
        is_author = obj.author == request.user
        return is_board_member and is_author
      return is_board_member