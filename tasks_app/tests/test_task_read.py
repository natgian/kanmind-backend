from django.db.models import Count
from django.urls import reverse

from rest_framework import status

from boards_app.tests.base import BoardBaseTestCase
from tasks_app.api.serializers import CommentSerializer, TaskDetailSerializer
from tasks_app.models import Comment, Task

class TaskReadTests(BoardBaseTestCase):
  """Tests for listing tasks, retrieving task details and viewing task comments."""
  def test_list_assigned_to_me_tasks_200_success(self):
    """Ensure an authenticated user can list all tasks assigned to them."""
    url = reverse("task-assigned-to-me")
    self.client.credentials(HTTP_AUTHORIZATION="Token " + self.member_token.key)

    response = self.client.get(url)

    self.assertEqual(response.status_code, status.HTTP_200_OK)

    user = self.member_user
    tasks_in_db = Task.objects.annotate(annotated_comments_count=Count("comments", dinstinct=True)).filter(assignee=user).distinct()
    expected_data = TaskDetailSerializer(tasks_in_db, many=True).data

    self.assertEqual(response.data, expected_data)


  def test_list_assigned_to_me_tasks_401_fail_not_authenticated(self):
    """Ensure listing assigned tasks fails with an error 401 if the user is not authenticated."""
    url = reverse("task-assigned-to-me")

    response = self.client.get(url)

    self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


  def test_list_reviewing_tasks_200_success(self):
    """Ensure an authenticated user can list all tasks where they are the reviewer."""
    url = reverse("task-reviewing")
    self.client.credentials(HTTP_AUTHORIZATION="Token " + self.owner_token.key)

    response = self.client.get(url)

    self.assertEqual(response.status_code, status.HTTP_200_OK)

    user = self.member_user
    tasks_in_db = Task.objects.annotate(annotated_comments_count=Count("comments", dinstinct=True)).filter(reviewer=user).distinct()
    expected_data = TaskDetailSerializer(tasks_in_db, many=True).data

    self.assertEqual(response.data, expected_data)


  def test_list_reviewing_tasks_401_fail_not_authenticated(self):
    """
    Ensure listing tasks where the user is the reviewer fails with an error 401 
    if the user is not authenticated.
    """
    url = reverse("task-reviewing")

    response = self.client.get(url)

    self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


  def test_list_task_comments_200_success(self):
    """Ensure an authenticated board member can list comments for a task on that board."""
    url = reverse("task-comments-list", kwargs={"task_id": self.task_one.pk})
    self.client.credentials(HTTP_AUTHORIZATION="Token " + self.member_token.key)

    response = self.client.get(url)

    self.assertEqual(response.status_code, status.HTTP_200_OK)

    comments_in_db = Comment.objects.filter(task_id=self.task_one.pk)
    expected_data = CommentSerializer(comments_in_db, many=True).data

    self.assertEqual(response.data, expected_data)


  def test_list_task_comments_401_fail_not_authenticated(self):
    """Ensure listing task comments fails with an error 401 if the user is not authenticated."""
    url = reverse("task-comments-list", kwargs={"task_id": self.task_one.pk})
    
    response = self.client.get(url)
    
    self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


  def test_list_task_comments_403_fail_forbidden(self):
    """
    Ensure listing task comments fails with an error 403 if the user is not a member of the board the 
    the task belongs to.
    """
    url = reverse("task-comments-list", kwargs={"task_id": self.task_one.pk})
    self.client.credentials(HTTP_AUTHORIZATION="Token " + self.not_member_token.key)

    response = self.client.get(url)

    self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


  def test_list_task_comments_404_fail_not_found(self):
    """Ensure listing task comments fails with an error 404 if the task is not found."""
    url = reverse("task-comments-list", kwargs={"task_id": 99999})
    self.client.credentials(HTTP_AUTHORIZATION="Token " + self.member_token.key)

    response = self.client.get(url)

    self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

