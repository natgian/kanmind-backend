from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from .models import CustomUser

class CustomUserCreationForm(forms.ModelForm):
    """Custom form for creating a new user in the admin panel."""
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = CustomUser
        fields = ("fullname", "email", "password")

    def save(self, commit=True):
        """Hash the password before saving the user."""

        # Create the user object in the memory
        user = super().save(commit=False)
        # Set the hashed password
        user.set_password(self.cleaned_data["password"]) 
        if commit:
            user.save()
        return user


class CustomUserChangeForm(UserChangeForm):
    """
    Custom form used for editing an existing user.

    Inherits from UserChangeForm to ensure the password is encrypted and provides a button to change it securely.
    """
    class Meta:
        model = CustomUser
        fields = ("email", "fullname")


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Configuration for CustomUser in admin panel."""
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    list_display = ("fullname", "email", "is_staff", "is_active")
    search_fields = ("fullname", "email")
    ordering = ("fullname",)

    add_fieldsets = (
        (None, {"fields": ("fullname", "email", "password")}),
    )

    fieldsets = (
        ("Account Details", {"fields": ("fullname", "email", "password")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser")})
    )



