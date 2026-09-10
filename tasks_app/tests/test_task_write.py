from django.db.models import Count
from django.urls import reverse

from rest_framework import status

from boards_app.tests.base import BoardBaseTestCase
from tasks_app.api.serializers import CommentSerializer, TaskCreateAndUpdateSerializer, TaskDetailSerializer
from tasks_app.models import Comment, Task

class TaskWriteTests(BoardBaseTestCase):
  """Tests for creating, updating and deleting tasks and comments."""
  def test_create_task_201_success(self):
    """Ensure a task can be created if the user is authenticated and a member of the board with the given ID."""
    url = reverse("task-list")
    self.client.credentials(HTTP_AUTHORIZATION="Token " + self.member_token.key)
    data = {
      "board": self.board_with_member.id,
      "title": "Create Task Test",
      "description": "Test creating a task.",
      "status": "to-do",
      "priority": "high",
      "assignee_id": self.member_user.id,
      "reviewer_id": self.owner_user.id,
      "due_date": "2026-09-27"
    }
    
    response = self.client.post(url, data, format="json")
    
    self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    new_task_id = response.data["id"]
    task_in_db = Task.objects.annotate(annotated_comments_count=Count("comments", distinct=True)).get(id=new_task_id)
    expected_data = TaskDetailSerializer(task_in_db).data

    self.assertEqual(response.data, expected_data)


  def test_create_task_400_fail_invalid_data(self):
    """Ensure creating a task fails with an error 400 if the data is invalid."""
    url = reverse("task-list")
    self.client.credentials(HTTP_AUTHORIZATION="Token " + self.member_token.key)
    data = {}
        
    response = self.client.post(url, data, format="json")
        
    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    required_fields = ["board", "title", "description", "due_date"]
    for field in required_fields:
      self.assertIn(field, response.data)


  def test_create_task_401_fail_not_authenticated(self):
    """Ensure creating a task fails with an error 401 if the user is not authenticated."""
    url = reverse("task-list")
    data = {
      "board": self.board_with_member.id,
      "title": "Create Task Test",
      "description": "Test creating a task.",
      "status": "to-do",
      "priority": "high",
      "assignee_id": self.member_user.id,
      "reviewer_id": self.owner_user.id,
      "due_date": "2026-09-27"
    }
        
    response = self.client.post(url, data, format="json")
        
    self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


  def test_create_task_403_fail_forbiddeen(self):
    """Ensure creating a task fails with an error 403 if the user is not a member of the board."""
    url = reverse("task-list")
    self.client.credentials(HTTP_AUTHORIZATION="Token " + self.not_member_token.key)
    data = {
      "board": self.board_with_member.id,
      "title": "Create Task Test",
      "description": "Test creating a task.",
      "status": "to-do",
      "priority": "high",
      "assignee_id": self.member_user.id,
      "reviewer_id": self.owner_user.id,
      "due_date": "2026-09-27"
    }
        
    response = self.client.post(url, data, format="json")
        
    self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


  def test_create_task_404_fail_not_found(self):
    """Ensure creating a task fails with an error 404 if the board is not found with the given ID."""
    url = reverse("task-list")
    self.client.credentials(HTTP_AUTHORIZATION="Token " + self.member_token.key)
    data = {
      "board": 9999,
      "title": "Create Task Test",
      "description": "Test creating a task.",
      "status": "to-do",
      "priority": "high",
      "assignee_id": self.member_user.id,
      "reviewer_id": self.owner_user.id,
      "due_date": "2026-09-27"
    }
        
    response = self.client.post(url, data, format="json")
        
    self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


  def test_create_task_comment_201_success(self):
    """Ensure an authenticated board member can successfully add a comment to a task."""
    url = reverse("task-comments-list", kwargs={"task_id": self.task_one.pk})
    self.client.credentials(HTTP_AUTHORIZATION="Token " + self.member_token.key)
    data = {"content": "This is a test comment for task number one."}

    response = self.client.post(url, data, format="json")

    self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    new_comment_id = response.data["id"]
    comment_in_db = Comment.objects.get(id=new_comment_id)
    expected_data = CommentSerializer(comment_in_db).data

    self.assertEqual(response.data, expected_data)


  def test_create_task_comment_400_fail_invalid_data(self):
    """Ensure creating a comment fails with an error 400 if the data is invalid."""
    url = reverse("task-comments-list", kwargs={"task_id": self.task_one.pk})
    self.client.credentials(HTTP_AUTHORIZATION="Token " + self.member_token.key)
    data = {"content": ""}

    response = self.client.post(url, data, format="json")

    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

  
  def test_create_task_comment_401_fail_not_authenticated(self):
    """Ensure creating a comment fails with an error 401 if the user is not authenticated."""
    url = reverse("task-comments-list", kwargs={"task_id": self.task_one.pk})
    data = {"content": "This is a test comment for task number one."}

    response = self.client.post(url, data, format="json")

    self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

  
  def test_create_task_comment_403_fail_forbidden(self):
    """Ensure creating a comment fails with an error 403 if the user is not a member of the board."""
    url = reverse("task-comments-list", kwargs={"task_id": self.task_one.pk})
    self.client.credentials(HTTP_AUTHORIZATION="Token " + self.not_member_token.key)
    data = {"content": "This is a test comment for task number one."}

    response = self.client.post(url, data, format="json")

    self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
  

  def test_create_task_comment_404_fail_not_found(self):
    """Ensure creating a comment fails with an error 404 if the task is not found with the given ID."""
    url = reverse("task-comments-list", kwargs={"task_id": 9999})
    self.client.credentials(HTTP_AUTHORIZATION="Token " + self.member_token.key)
    data = {"content": "This is a test comment for task number one."}

    response = self.client.post(url, data, format="json")

    self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


  def test_update_task_200_success(self):
    """Ensure a member of the board can update a task."""
    url = reverse("task-detail", kwargs={"pk": self.task_one.pk})
    self.client.credentials(HTTP_AUTHORIZATION="Token " + self.member_token.key)
    updated_data = {"status": "done"}

    response = self.client.patch(url, updated_data, format="json")

    self.assertEqual(response.status_code, status.HTTP_200_OK)

    new_task_id = response.data["id"]
    task_in_db = Task.objects.annotate(annotated_comments_count=Count("comments", distinct=True)).get(id=new_task_id)
    expected_data = TaskDetailSerializer(task_in_db).data
    expected_data.pop("comments_count")
    expected_data.pop("board")

    self.assertEqual(response.data, expected_data)
    

  def test_update_task_400_fail_invalid_data(self):
    """Ensure updating a task fails with an error 400 if the data is invalid."""
    url = reverse("task-detail", kwargs={"pk": self.task_one.pk})
    self.client.credentials(HTTP_AUTHORIZATION="Token " + self.member_token.key)
    updated_data = {"status": "-"}

    response = self.client.patch(url, updated_data, format="json")

    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


  def test_update_task_401_fail_not_authenticated(self):
    """Ensure updating a task fails with an error 401 if the user is not authenticated."""
    url = reverse("task-detail", kwargs={"pk": self.task_one.pk})
    updated_data = {"status": "done"}

    response = self.client.patch(url, updated_data, format="json")

    self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


  def test_update_task_403_fail_forbidden(self):
    """Ensure updating a task fails with an error 403 if the user is not a member of the board."""
    url = reverse("task-detail", kwargs={"pk": self.task_one.pk})
    self.client.credentials(HTTP_AUTHORIZATION="Token " + self.not_member_token.key)
    updated_data = {"status": "done"}

    response = self.client.patch(url, updated_data, format="json")

    self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


  def test_update_task_404_fail_not_found(self):
    """Ensure updating a task fails with an error 404 if the task with the given ID is not found."""
    url = reverse("task-detail", kwargs={"pk": 9999})
    self.client.credentials(HTTP_AUTHORIZATION="Token " + self.member_token.key)
    updated_data = {"status": "done"}

    response = self.client.patch(url, updated_data, format="json")

    self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


  def test_delete_task_204_success(self):
    """Ensure a task can be deleted by a board member."""
    url = reverse("task-detail", kwargs={"pk": self.task_one.pk})
    self.client.credentials(HTTP_AUTHORIZATION="Token " + self.member_token.key)

    response = self.client.delete(url)

    self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


  def test_delete_task_401_fail_not_authenticated(self):
    """Ensure deleting a task fails with an error 401 if the user is not authenticated."""
    url = reverse("task-detail", kwargs={"pk": self.task_one.pk})

    response = self.client.delete(url)

    self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


  def test_delete_task_403_fail_forbidden(self):
    """Ensure deleting a task fails with an error 403 if the user not a board member."""
    url = reverse("task-detail", kwargs={"pk": self.task_one.pk})
    self.client.credentials(HTTP_AUTHORIZATION="Token " + self.not_member_token.key)

    response = self.client.delete(url)

    self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


  def test_delete_task_404_fail_not_found(self):
    """Ensure deleting a task fails with an error 404 if the task with the given ID is not found."""
    url = reverse("task-detail", kwargs={"pk": 9999})
    self.client.credentials(HTTP_AUTHORIZATION="Token " + self.member_token.key)

    response = self.client.delete(url)

    self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


  def test_delete_task_comment_204_success(self):
    """Ensure a comment can only be deleted by it's author."""
    url = reverse("task-comments-detail", kwargs={"task_id": self.task_one.pk, "pk": self.comment_three.pk})
    self.client.credentials(HTTP_AUTHORIZATION="Token " + self.member_token.key)

    response = self.client.delete(url)

    self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


  def test_delete_task_comment_401_fail_not_authenticated(self):
    """Ensure deleting a comment fails with an error 401 if the user is not authenticated."""
    url = reverse("task-comments-detail", kwargs={"task_id": self.task_one.pk, "pk": self.comment_three.pk})

    response = self.client.delete(url)

    self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


  def test_delete_task_comment_403_fail_forbidden(self):
    """Ensure deleting a comment fails with an error 403 if user is not the author of the comment."""
    url = reverse("task-comments-detail", kwargs={"task_id": self.task_one.pk, "pk": self.comment_three.pk})
    self.client.credentials(HTTP_AUTHORIZATION="Token " + self.not_member_token.key)

    response = self.client.delete(url)

    self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


  def test_delete_task_comment_404_fail_task_not_found(self):
    """Ensure deleting a comment fails with an error 404 if the task with the given ID is not found."""
    url = reverse("task-comments-detail", kwargs={"task_id": 9999, "pk": self.comment_three.pk})
    self.client.credentials(HTTP_AUTHORIZATION="Token " + self.member_token.key)

    response = self.client.delete(url)

    self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


  def test_delete_task_comment_404_fail_comment_not_found(self):
    """Ensure deleting a comment fails with an error 404 if the comment with the given ID is not found."""
    url = reverse("task-comments-detail", kwargs={"task_id": self.task_one.pk, "pk": 9999})
    self.client.credentials(HTTP_AUTHORIZATION="Token " + self.member_token.key)

    response = self.client.delete(url)

    self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)



  
