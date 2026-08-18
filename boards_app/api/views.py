from django.db.models import Q, Count

from rest_framework import viewsets, permissions
from rest_framework.response import Response

from .serializers import BoardSerializer
from .permissions import IsBoardOwnerOrMember
from ..models import Board

class BoardViewSet(viewsets.ModelViewSet):
  """
  ViewSet for handling Board creation, retrieval, updates and deletion.

  Enforces authentication and permissions for all actions.
  """
  serializer_class = BoardSerializer
  permission_classes = [permissions.IsAuthenticated, IsBoardOwnerOrMember]

  def get_queryset(self):
    """
    Return boards where the user is owner or member.
    
    If the action is 'list', the queryset is annotated with calculated statistics for members, tickets (tasks) and specific task status/priority.
    """
    user = self.request.user
    queryset = Board.objects.filter(Q(owner=user) | Q(members=user)).distinct()

    if self.action == "list":
      return queryset.annotate(
        annotated_member_count=Count("members", distinct=True),
        annotated_ticket_count=Count("tasks", distinct=True),
        annotated_tasks_to_do_count=Count("tasks", filter=Q(tasks__status="to-do"), distinct=True),
        annotated_tasks_high_prio_count=Count("tasks", filter=Q(tasks__priority="high"), distinct=True)
      )
    return queryset






    