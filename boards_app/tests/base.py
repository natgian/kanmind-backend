from django.contrib.auth import get_user_model

from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from boards_app.models import Board

User = get_user_model()

class BoardBaseTestCase(APITestCase):
  def setUp(self):
    """Set up test user data and authentication before each test method runs."""
    # Create owner and generate token
    self.owner_user = User.objects.create_user(fullname="Board Owner", email="owner@mail.com", password="ownerPassword")
    self.owner_token = Token.objects.create(user=self.owner_user)
    # Create member and generate token
    self.member_user = User.objects.create_user(fullname="Board Member", email="member@mail.com", password="memberPassword")
    self.member_token = Token.objects.create(user=self.member_user)
    # Create test boards
    self.board_with_member = Board.objects.create(title="Test Board with member", owner=self.owner_user)
    self.board_with_member.members.add(self.member_user)
    self.board_without_member = Board.objects.create(title="Test Board without member", owner=self.owner_user)