from django.db.models import Count
from django.contrib.auth import get_user_model

from rest_framework import viewsets, permissions, status
from rest_framework.response import Response

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
    """Update an existing task."""
    task = self.get_object()
    write_serializer = self.get_serializer(task, data=request.data, partial=True)
    write_serializer.is_valid(raise_exception=True)
    updated_task = write_serializer.save()

    annotated_task = self.get_queryset().get(id=updated_task.id)
    response_serializer = TaskDetailSerializer(annotated_task, context={"request": request})
    response_data = response_serializer.data

    if "comments_count" in response_data:
      del response_data["comments_count"]

    return Response(response_data, status=status.HTTP_200_OK)






#   {
#   "title": "Code-Review abschließen",
#   "description": "Den PR fertig prüfen und Feedback geben",
#   "status": "done",
#   "priority": "high",
#   "assignee_id": 13,
#   "reviewer_id": 1,
#   "due_date": "2025-02-28"
# }

