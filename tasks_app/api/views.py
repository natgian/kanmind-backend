from django.contrib.auth import get_user_model
from django.db.models import Count
from django.shortcuts import get_object_or_404

from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import Comment, Task
from .permissions import IsBoardMember
from .serializers import CommentSerializer, TaskCreateAndUpdateSerializer, TaskDetailSerializer

User = get_user_model()

class TaskViewSet(viewsets.ModelViewSet):
  """
  ViewSet for handling Task creation, retrieval, updates and deletion.

  Enforces authentication and board mempership for all actions.
  """
  permission_classes = [permissions.IsAuthenticated, IsBoardMember]

  def get_serializer_class(self):
    """
    Define which serializer should be used for each action.
    
    Return TaskDetailSerializer for safe read actions (list, retrieve) and TaskCreateAndUpdateSerializer
    for write operations.
    """
    if self.action in ["list", "retrieve"]:
      return TaskDetailSerializer
    return TaskCreateAndUpdateSerializer

  def get_queryset(self):
    """Return tasks only for boards where the current user is a member."""
    base_queryset = Task.objects.annotate(annotated_comments_count=Count("comments", distinct=True)).distinct()

    # For actions or individual object, allow access to all tasks so it can return a clean 403 error
    if self.action in ["retrieve", "update", "partial_update", "destroy"]:
      return base_queryset
    
    user =self.request.user
    return base_queryset.filter(board__members=user)

  def create(self, request, *args, **kwargs):
    """Create a new task and return full details."""
    write_serializer = self.get_serializer(data=request.data)
    write_serializer.is_valid(raise_exception=True)
    new_task = write_serializer.save()

    annotated_task = self.get_queryset().get(id=new_task.id)
    response_serializer = TaskDetailSerializer(annotated_task, context={"request": request})
    return Response(response_serializer.data, status=status.HTTP_201_CREATED)

  def update(self, request, *args, **kwargs):
    """
    Update an existing task.

    Return the updated task details excluding 'board' and 'comments_count'.    
    """
    task = self.get_object()
    write_serializer = self.get_serializer(task, data=request.data, partial=True)
    write_serializer.is_valid(raise_exception=True)
    updated_task = write_serializer.save()

    annotated_task = self.get_queryset().get(id=updated_task.id)
    response_serializer = TaskDetailSerializer(annotated_task, context={"request": request})
    response_data = response_serializer.data

    response_data.pop("comments_count", None)
    response_data.pop("board", None) 

    return Response(response_data, status=status.HTTP_200_OK)

  @action(detail=False, methods=["get"], url_path="assigned-to-me")
  def assigned_to_me(self, request):
    """List the tasks assigned to the authenticated user."""
    assigned_tasks = self.get_queryset().filter(assignee=request.user)
    response_serializer = TaskDetailSerializer(assigned_tasks, many=True, context={"request": request})
    return Response(response_serializer.data, status=status.HTTP_200_OK)
  
  @action(detail=False, methods=["get"], url_path="reviewing")
  def reviewing(self, request):
    """List the tasks where the authenticated user is the reviewer."""
    reviewing_tasks = self.get_queryset().filter(reviewer=request.user)
    response_serializer = TaskDetailSerializer(reviewing_tasks, many=True, context={"request": request})
    return Response(response_serializer.data, status=status.HTTP_200_OK)


class CommentViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,mixins.DestroyModelMixin, viewsets.GenericViewSet):
  """
  ViewSet for handling Comment creation and retrieval.
  
  Enforces authentication and board membership for all actions.
  """
  permission_classes = [permissions.IsAuthenticated, IsBoardMember]
  serializer_class = CommentSerializer
  queryset = Comment.objects.all()

  def perform_create(self, serializer):
    """Save the comment in the database with the current user as author."""
    author = self.request.user
    task_id = self.kwargs.get("task_id")
    task = get_object_or_404(Task, id=task_id)
    serializer.save(author=author, task=task)

  def get_queryset(self):
    """List comments on the current task."""
    current_task_id = self.kwargs.get("task_id")
    filtered_queryset = self.queryset.filter(task_id=current_task_id)
    return filtered_queryset
  

