from rest_framework import permissions

class IsBoardOwnerOrMember(permissions.BasePermission):
  """Allows access only if the user is the owner or a member of the board."""
  def has_object_permission(self, request, view, obj):
    is_owner = obj.owner == request.user
    is_member = obj.members.filter(id=request.user.id).exists()

    return is_owner or is_member