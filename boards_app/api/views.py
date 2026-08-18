from django.db.models import Q, Count, Prefetch

from rest_framework import viewsets, permissions
from rest_framework.response import Response

from .serializers import BoardSerializer, BoardDetailSerializer
from .permissions import IsBoardOwnerOrMember
from ..models import Board
from tasks_app.models import Task

class BoardViewSet(viewsets.ModelViewSet):
  """
  ViewSet for handling Board creation, retrieval, updates and deletion.

  Enforces authentication and permissions for all actions.
  """
  permission_classes = [permissions.IsAuthenticated, IsBoardOwnerOrMember]

  def get_serializer_class(self):
    """Define which serializer should be used for each action."""
    if self.action == "retrieve":
      return BoardDetailSerializer
    return BoardSerializer

  def get_queryset(self):
    """
    Return boards based on the requested action.
    
    If the action is:
    - 'list': return boards where the user is owner or member, annotated with specific statistics like member and
    tickets (tasks) counts.
    - 'retrieve': return all boards to allow permission checks, while prefetching members and tasks for better performance. Tasks are annotated to include the calculated comment counts.
    """
    user = self.request.user
    
    if self.action == "list":
      queryset = Board.objects.filter(Q(owner=user) | Q(members=user)).distinct()
      return queryset.annotate(
        annotated_member_count=Count("members", distinct=True),
        annotated_ticket_count=Count("tasks", distinct=True),
        annotated_tasks_to_do_count=Count("tasks", filter=Q(tasks__status="to-do"), distinct=True),
        annotated_tasks_high_prio_count=Count("tasks", filter=Q(tasks__priority="high"), distinct=True)
      )
    elif self.action == "retrieve":
      tasks_with_comments = Task.objects.annotate(annotated_comments_count=Count("comments", distinct=True))
      return Board.objects.prefetch_related("members", Prefetch("tasks", queryset=tasks_with_comments))
    
    return Board.objects.all()






    