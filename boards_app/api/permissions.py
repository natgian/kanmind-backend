from rest_framework import permissions

class IsBoardOwnerOrMember(permissions.BasePermission):
  """
  Allow access for 'retrieve' (GET detail) and 'partial_update' (PATCH) requests only if the user is the owner or a member of the board.
  
  For 'destroy' (DELETE) request the user must be the owner of the board.
  """
  def has_object_permission(self, request, view, obj):
    is_owner = obj.owner == request.user
    is_member = obj.members.filter(id=request.user.id).exists()

    if view.action in ["retrieve", "partial_update"]:
      return is_owner or is_member

    if view.action in ["destroy"]:
      return is_owner

    return False