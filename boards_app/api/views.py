from django.db.models import Q, Count, Prefetch
from django.contrib.auth import get_user_model

from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import BoardSerializer, BoardDetailSerializer, BoardUpdateSerializer, EmailCheckSerializer
from .permissions import IsBoardOwnerOrMember
from ..models import Board

from tasks_app.models import Task
from auth_app.api.serializers import UserProfileSerializer

User = get_user_model()

class BoardViewSet(viewsets.ModelViewSet):
  """
  ViewSet for handling Board creation, retrieval, updates and deletion.

  Enforces authentication and permissions for all actions.
  """
  permission_classes = [permissions.IsAuthenticated, IsBoardOwnerOrMember]

  def get_serializer_class(self):
    """Return the appropriate serializer class based on the current action."""
    if self.action == "retrieve":
      return BoardDetailSerializer
    elif self.action in ["update", "partial_update"]:
      return BoardUpdateSerializer
    return BoardSerializer

  def get_queryset(self):
    """
    Return boards based on the requested action.
    
    If the action is:
    - 'list' / 'create': filter boards where the user is the owner or a member. Annotates each board with member, ticket and task-specific counts.
    - 'retrieve': prefetch members and tasks (including annotated comment counts) for the specific board to optimize performance.
    """
    user = self.request.user
    
    if self.action in ["list", "create"]:
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

  def perform_create(self, serializer):
    """
    Save the new board instance and reload it with annotated data.
    
    Ensures that the response contains the annotated fields calculated in 'get_queryset' immediately after creation.
    """
    board = serializer.save()
    serializer.instance = self.get_queryset().get(pk=board.pk)


class EmailCheckView(APIView):
  """View to return user information (id, email, fullname) based on the email."""
  permission_classes = [permissions.IsAuthenticated]

  def get(self, request, format=None):
        """
        Check if an email exists and return user details.

        Expects 'email' as a query paramater.
        """
        serializer = EmailCheckSerializer(data=request.query_params)

        if serializer.is_valid():
          validated_email = serializer.validated_data["email"]
          found_user = User.objects.filter(email=validated_email).first()
          if found_user:
            user_serializer = UserProfileSerializer(found_user)
            return Response(user_serializer.data, status=status.HTTP_200_OK)
          else:
            return Response({"detail": "Email not found. The email address does not exist."}, status=status.HTTP_404_NOT_FOUND)
        else:
          return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        








    