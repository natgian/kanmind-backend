from rest_framework import permissions

class IsBoardOwnerOrMember(permissions.BasePermission):
  """
  Allows access for GET and PATCH requests only if the user is the owner or a member of the board.
  
  For DELETE request the user must be the owner of the board.
  """
  def has_object_permission(self, request, view, obj):
    is_owner = obj.owner == request.user
    is_member = obj.members.filter(id=request.user.id).exists()

    if view.action in ["retrieve", "partial_update"]:
      return is_owner or is_member

    return is_owner