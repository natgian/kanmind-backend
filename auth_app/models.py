from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from rest_framework.authtoken.models import TokenProxy

class CustomUserManager(BaseUserManager):
    """Custom manager where email is the unique identifier for authentication instead of username."""
    def create_user(self, email, fullname, password=None, **extra_fields):
        """Create and save a user with the given email and fullname."""
        if not email:
            raise ValueError("The email field must be set.")
        email = self.normalize_email(email)
        user = self.model(email=email, fullname=fullname, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, fullname, password=None, **extra_fields):
        """Create and save a superuser with the given email and fullname."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")
        return self.create_user(email, fullname, password, **extra_fields)


class CustomUser(AbstractUser):
    """
    Custom user model where email is the unique identifier for authentification instead of username.
    
    Includes required fullname field.
    """
    username = None
    email = models.EmailField(unique=True)
    fullname = models.CharField(max_length=255)
    # Link with the custom manager
    objects = CustomUserManager()
    # Use email as primary unique identifier 
    USERNAME_FIELD = "email"
    # Set fullname as a required field
    REQUIRED_FIELDS = ["fullname"]

    def __str__(self):
        return self.fullname


class CustomToken(TokenProxy):
    """
    Represent a proxy token model to display Tokens under the custom User Management section in the Django
    Admin Panel.
    """
    class Meta:
        proxy = True
        verbose_name = "Token"
        verbose_name_plural = "Tokens"


