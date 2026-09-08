from django.db.models import Count, Q, Prefetch
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status

from auth_app.api.serializers import UserProfileSerializer
from boards_app.api.serializers import BoardSerializer, BoardDetailSerializer
from boards_app.models import Board
from boards_app.tests.base import BoardBaseTestCase
from tasks_app.models import Task

User = get_user_model()

class BoardReadTests(BoardBaseTestCase):
  """Tests for listing boards and retrieving board details."""
  def test_list_boards_200_is_owner(self):
    """Ensure a board owner can successfully list all boards they own or are a member of."""
    url = reverse("board-list")
    self.client.credentials(HTTP_AUTHORIZATION="Token " + self.owner_token.key)
    
    response = self.client.get(url)

    self.assertEqual(response.status_code, status.HTTP_200_OK)

    user = self.owner_user
    boards_in_db = Board.objects.filter(Q(owner=user) | Q(members=user)).distinct().annotate(
        annotated_member_count=Count("members", distinct=True),
        annotated_ticket_count=Count("tasks", distinct=True),
        annotated_tasks_to_do_count=Count("tasks", filter=Q(tasks__status="to-do"), distinct=True),
        annotated_tasks_high_prio_count=Count("tasks", filter=Q(tasks__priority="high"), distinct=True)
    )
    expected_data = BoardSerializer(boards_in_db, many=True).data

    self.assertEqual(response.data, expected_data)


  def test_list_boards_200_is_member(self):
    """Ensure a board member can successfully list all boards they are a member of."""
    url = reverse("board-list")
    self.client.credentials(HTTP_AUTHORIZATION="Token " + self.member_token.key)
    
    response = self.client.get(url)

    self.assertEqual(response.status_code, status.HTTP_200_OK)


  def test_list_boards_401_fail_not_authenticated(self):
    """Ensure fails with an error 401 if the user is not authenticated."""
    url = reverse("board-list")

    response = self.client.get(url)

    self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


  def test_detail_board_200_success_is_owner(self):
    """Ensure a board owner can successfully list details of a board."""
    url = reverse("board-detail", kwargs={"pk": self.board_with_member.pk})
    self.client.credentials(HTTP_AUTHORIZATION="Token " + self.owner_token.key)
        
    response = self.client.get(url)

    self.assertEqual(response.status_code, status.HTTP_200_OK)


  def test_detail_board_200_success_is_owner(self):
    """Ensure a board owner can successfully list details of a board he owns."""
    url = reverse("board-detail", kwargs={"pk": self.board_with_member.pk})
    self.client.credentials(HTTP_AUTHORIZATION="Token " + self.owner_token.key)
        
    response = self.client.get(url)

    self.assertEqual(response.status_code, status.HTTP_200_OK)

    tasks_with_comments = Task.objects.annotate(annotated_comments_count=Count("comments", distinct=True))
    board_in_db = Board.objects.prefetch_related("members", Prefetch("tasks", queryset=tasks_with_comments)).get(id=self.board_with_member.id)
    expected_data = BoardDetailSerializer(board_in_db).data

    self.assertEqual(response.data, expected_data)


  def test_detail_board_200_success_is_member(self):
    """Ensure a board member can successfully list details of a board he is a member of."""
    url = reverse("board-detail", kwargs={"pk": self.board_with_member.pk})
    self.client.credentials(HTTP_AUTHORIZATION="Token " + self.member_token.key)
        
    response = self.client.get(url)

    self.assertEqual(response.status_code, status.HTTP_200_OK)


  def test_detail_board_401_fail_not_authenticated(self):
    """Ensure fails with an error 401 if the user is not authenticated."""
    url = reverse("board-detail", kwargs={"pk": self.board_with_member.pk})
        
    response = self.client.get(url)

    self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


  def test_detail_board_403_fail_forbidden(self):
    """Ensure fails with an error 403 if the user is not owner or member of the board."""
    url = reverse("board-detail", kwargs={"pk": self.board_without_member.pk})
    self.client.credentials(HTTP_AUTHORIZATION="Token " + self.member_token.key)
        
    response = self.client.get(url)

    self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


  def test_detail_board_404_not_found(self):
    """Ensure fails with an error 404 if the board with the given ID does not exist."""
    url = reverse("board-detail", kwargs={"pk": 99999})
    self.client.credentials(HTTP_AUTHORIZATION="Token " + self.owner_token.key)
        
    response = self.client.get(url)

    self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


  def test_email_check_200_success(self):
    """Ensure that the endpoint identifies an existing email and returns user details."""
    url = reverse("email-check")
    self.client.credentials(HTTP_AUTHORIZATION="Token " + self.owner_token.key)

    response = self.client.get(url, data={"email": self.owner_user.email})

    self.assertEqual(response.status_code, status.HTTP_200_OK)

    expected_data = UserProfileSerializer(self.owner_user).data

    self.assertEqual(response.data, expected_data)


  def test_email_check_400_fail_invalid_data(self):
    """Ensure the check fails if the given email is invalid."""
    url = reverse("email-check")
    self.client.credentials(HTTP_AUTHORIZATION="Token " + self.owner_token.key)
    
    response = self.client.get(url, data={"email": "test@test."})
    
    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


  def test_email_check_401_fail_not_authenticated(self):
    """Ensure the email check fails if the user is not authenticated."""
    url = reverse("email-check")
    
    response = self.client.get(url, data={"email": self.owner_user.email})
    
    self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


  def test_email_check_404_fail_not_found(self):
    """Ensure the check fails if the email is not found."""
    url = reverse("email-check")
    self.client.credentials(HTTP_AUTHORIZATION="Token " + self.owner_token.key)
    
    response = self.client.get(url, data={"email": "test@test.com"})
    
    self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)