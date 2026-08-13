from django.db import models
from django.conf import settings

class Board(models.Model):
  """Model representing a board."""
  title = models.CharField(max_length=50)
  owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="owned_boards")
  members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="boards", blank=True)

  def __str__(self):
    return self.title