from rest_framework import permissions

class IsBoardMember(permissions.BasePermission):
  """
  Allows access for GET and PATCH requests only if the user is a member of the board.
  """
  def has_object_permission(self, request, view, obj):
    is_member = obj.board.members.filter(id=request.user.id).exists()
    return is_member