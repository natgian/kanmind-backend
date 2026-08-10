from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
  """
  Custom user model that extends Django's AbstractUser to include a fullname field required for the registration.
  """
  
  fullname = models.CharField(max_length=255)
