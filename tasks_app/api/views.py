from django.db.models import Count
from django.contrib.auth import get_user_model

from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from ..models import Task
from .permissions import IsBoardMember
from .serializers import TaskDetailSerializer, TaskCreateAndUpdateSerializer

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
    user =self.request.user
    return Task.objects.filter(board__members=user).annotate(annotated_comments_count=Count("comments", distinct=True)).distinct()

  def create(self, request, *args, **kwargs):
    """
    Create a new task.
    
    Check if the input data is valid, save the new task, then return the full task details in the response.
    """
    write_serializer = self.get_serializer(data=request.data)
    write_serializer.is_valid(raise_exception=True)
    new_task = write_serializer.save()
    annotated_task = self.get_queryset().get(id=new_task.id)
    response_serializer = TaskDetailSerializer(annotated_task, context={"request": request})
    return Response(response_serializer.data, status=status.HTTP_201_CREATED)

