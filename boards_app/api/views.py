from django.db.models import Q

from rest_framework import viewsets, permissions
from rest_framework.response import Response

from .serializers import BoardSerializer
from .permissions import IsBoardOwnerOrMember
from ..models import Board

class BoardViewSet(viewsets.ModelViewSet):
  """"""
  serializer_class = BoardSerializer
  permission_classes = [permissions.IsAuthenticated, IsBoardOwnerOrMember]

  def get_queryset(self):
    """Return a queryset of boards where the user is owner or member."""
    user = self.request.user
    return Board.objects.filter(Q(owner=user) | Q(members=user)).distinct()






    