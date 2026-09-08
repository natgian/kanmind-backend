from django.db.models import Count, Q
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status

from boards_app.api.serializers import BoardSerializer, BoardUpdateSerializer
from boards_app.models import Board
from boards_app.tests.base import BoardBaseTestCase

User = get_user_model()

class BoardWriteTests(BoardBaseTestCase):
  """Tests for creating, updating and deleting boards."""

  def test_create_board_200_success(self):
    """
    Ensure board is successfully created.

    Check if the creator is successfully set as the owner.

    Return board details with annotated data.
    """
    url = reverse("board-list")
    self.client.credentials(HTTP_AUTHORIZATION="Token " + self.owner_token.key)
    data = {
      "title": "Create Test Board",
      "members": [self.owner_user.id, self.member_user.id]
    }

    response = self.client.post(url, data, format="json")

    self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    new_board_id = response.data["id"]
    board_in_db = Board.objects.filter(id=new_board_id).annotate(
      annotated_member_count=Count("members", distinct=True),
      annotated_ticket_count=Count("tasks", distinct=True),
      annotated_tasks_to_do_count=Count("tasks", filter=Q(tasks__status="to-do"), distinct=True),
      annotated_tasks_high_prio_count=Count("tasks", filter=Q(tasks__priority="high"), distinct=True)
      ).first()
    expected_data = BoardSerializer(board_in_db).data

    self.assertEqual(board_in_db.owner, self.owner_user)
    self.assertEqual(response.data, expected_data)


  def test_create_board_400_fail_invalid_data(self):
    """Ensure creating a board fails with an error 400 if the data is invalid."""
    url = reverse("board-list")
    self.client.credentials(HTTP_AUTHORIZATION="Token " + self.owner_token.key)
    data = {
      "title": "Create Test Board",
      "members": [13]
    }
  
    response = self.client.post(url, data, format="json")
  
    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


  def test_create_board_401_fail_not_authenticated(self):
    """Ensure creating a board fails with an error 401 if the user is not authenticated."""
    url = reverse("board-list")
    data = {
      "title": "Create Test Board",
      "members": [self.owner_user.id, self.member_user.id]
    }
     
    response = self.client.post(url, data, format="json")
     
    self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


  def test_update_board_200_success_is_owner(self):
    """Ensure board is successfully updated if the user is the owner of the board."""
    url = reverse("board-detail", kwargs={"pk": self.board_with_member.pk})
    self.client.credentials(HTTP_AUTHORIZATION="Token " + self.owner_token.key)
    updated_data = {
      "title": "Updated Board",
      "members": [self.owner_user.id, self.member_user.id]
    }

    response = self.client.patch(url, updated_data, format="json")

    self.assertEqual(response.status_code, status.HTTP_200_OK)

    board_in_db = Board.objects.get(id=self.board_with_member.pk)
    expected_data = BoardUpdateSerializer(board_in_db).data

    self.assertEqual(response.data, expected_data)


  def test_update_board_200_success_is_member(self):
    """Ensure board is successfully updated if the user is a member of the board."""
    url = reverse("board-detail", kwargs={"pk": self.board_with_member.pk})
    self.client.credentials(HTTP_AUTHORIZATION="Token " + self.member_token.key)
    updated_data = {
      "title": "Updated Board",
      "members": [self.owner_user.id, self.member_user.id]
    }

    response = self.client.patch(url, updated_data, format="json")

    self.assertEqual(response.status_code, status.HTTP_200_OK)


  def test_update_board_400_fail_invalid_data(self):
    """Ensure updating a board fails with an error 400 if the updated data is invalid."""
    url = reverse("board-detail", kwargs={"pk": self.board_with_member.pk})
    self.client.credentials(HTTP_AUTHORIZATION="Token " + self.owner_token.key)
    updated_data = {
      "title": "Updated Board",
      "members": [12]
    }

    response = self.client.patch(url, updated_data, format="json")

    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


  def test_update_board_401_fail_not_authenticated(self):
    """Ensure updating a board fails with an error 401 if the user is not authenticated."""
    url = reverse("board-detail", kwargs={"pk": self.board_with_member.pk})
    updated_data = {
      "title": "Updated Board",
      "members": [self.owner_user.id, self.member_user.id]
    }

    response = self.client.patch(url, updated_data, format="json")

    self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


  def test_update_board_403_fail_forbidden(self):
    """Ensure updating a board fails with an error 403 if the user is not the owner or a member of the board."""
    url = reverse("board-detail", kwargs={"pk": self.board_without_member.pk})
    self.client.credentials(HTTP_AUTHORIZATION="Token " + self.member_token.key)
    updated_data = {
      "title": "Updated Board",
      "members": [self.owner_user.id, self.member_user.id]
    }

    response = self.client.patch(url, updated_data, format="json")

    self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


  def test_update_board_404_fail_not_found(self):
    """Ensure updating a board fails with an error 404 if the board is not found with the given ID."""
    url = reverse("board-detail", kwargs={"pk": 99999})
    self.client.credentials(HTTP_AUTHORIZATION="Token " + self.owner_token.key)
    updated_data = {
      "title": "Updated Board",
      "members": [self.owner_user.id, self.member_user.id]
    }

    response = self.client.patch(url, updated_data, format="json")

    self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


  def test_delete_board_204_success_is_owner(self):
    """Ensure the board is deleted if the user is the owner of the board."""
    url = reverse("board-detail", kwargs={"pk": self.board_with_member.pk})
    self.client.credentials(HTTP_AUTHORIZATION="Token " + self.owner_token.key)

    response = self.client.delete(url)

    self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


  def test_delete_board_401_fail_not_authenticated(self):
    """Ensure deleting a board fails with an error 401 if the user is not authenticated."""
    url = reverse("board-detail", kwargs={"pk": self.board_with_member.pk})

    response = self.client.delete(url)

    self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


  def test_delete_board_403_fail_forbidden(self):
    """Ensure deleting a board fails with an error 403 if the user is not the owner of the board."""
    url = reverse("board-detail", kwargs={"pk": self.board_with_member.pk})
    self.client.credentials(HTTP_AUTHORIZATION="Token " + self.member_token.key)

    response = self.client.delete(url)

    self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


  def test_delete_board_404_fail_not_found(self):
    """Ensure deleting a board fails with an error 404 if the board is not found with the given ID."""
    url = reverse("board-detail", kwargs={"pk": 99999})
    self.client.credentials(HTTP_AUTHORIZATION="Token " + self.owner_token.key)

    response = self.client.delete(url)

    self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)