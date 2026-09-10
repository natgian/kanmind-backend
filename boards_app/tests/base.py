from django.contrib.auth import get_user_model

from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from boards_app.models import Board
from tasks_app.models import Comment, Task

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
    # Create a non member user and generate token
    self.not_member_user = User.objects.create_user(fullname="Not Member", email="not_member@mail.com", password="notMemberPassword")
    self.not_member_token = Token.objects.create(user=self.not_member_user)
    # Create test boards
    self.board_with_member = Board.objects.create(title="Test Board with member", owner=self.owner_user)
    self.board_with_member.members.add(self.member_user)
    self.board_without_member = Board.objects.create(title="Test Board without member", owner=self.owner_user)
    # Create test tasks
    self.task_one = Task.objects.create(board=self.board_with_member, title="Code Review", description="Do code review for feature X.", status="to-do", priority="medium", assignee=self.member_user, reviewer=self.owner_user, due_date="2026-09-28")
    self.task_two = Task.objects.create(board=self.board_with_member, title="Write Tests", description="Write tests for API endpoints.", status="in-progress", priority="high", assignee=self.member_user, reviewer=self.owner_user, due_date="2026-09-14")
    # Create test task comments
    self.comment_one = Comment.objects.create(task=self.task_one, author=self.member_user, content="This is a new comment.")
    self.comment_two = Comment.objects.create(task=self.task_one, author=self.member_user, content="This is a second comment.")
    self.comment_three = Comment.objects.create(task=self.task_one, author=self.member_user, content="This is a third comment.")