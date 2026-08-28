from django.db import models
from django.conf import settings
from boards_app.models import Board

class Task(models.Model):
  """Model representing a task."""
  # Choices for status
  class StatusChoices(models.TextChoices):
    TO_DO = "to-do", "To Do"
    IN_PROGRESS = "in-progress", "In Progress"
    REVIEW = "review", "Review"
    DONE = "done", "Done"

  # Choices for priority
  class PriorityChoices(models.TextChoices):
    LOW = "low", "Low"
    MEDIUM = "medium", "Medium"
    HIGH = "high", "High"

  title = models.CharField(max_length=100)
  description = models.TextField()
  due_date = models.DateField()
  status = models.CharField(max_length=15, choices=StatusChoices.choices, default=StatusChoices.TO_DO)
  priority = models.CharField(max_length=10, choices=PriorityChoices.choices, default=PriorityChoices.LOW)

  board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name="tasks")
  assignee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, related_name="assigned_tasks")
  reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, related_name="tasks_to_review")

  def __str__(self):
    return self.title


class Comment(models.Model):
  """Model representing a comment."""
  task = models.ForeignKey("Task", on_delete=models.CASCADE, related_name="comments")
  created_at = models.DateTimeField(auto_now_add=True)
  author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="authored_comments")
  content = models.TextField(max_length=500)

  class Meta:
    ordering = ["created_at"]

