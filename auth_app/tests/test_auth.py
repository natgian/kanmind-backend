from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

User = get_user_model()

class AuthTests(APITestCase):
  def setUp(self):
    """Set up test user data before each test method runs."""
    self.setup_user = User.objects.create_user(fullname="Setup User", email="setup-user@mail.com", password="setupPassword")


  def test_user_registration_201_success(self):
    """Ensure a user can register successfully with valid data and receives a token."""
    url = reverse("registration")
    data = {
      "fullname": "Example Username",
      "email": "example@mail.com",
      "password": "examplePassword",
      "repeated_password": "examplePassword"
    } 

    response = self.client.post(url, data, format="json")

    self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    new_user = User.objects.get(id=response.data["user_id"])
    token = Token.objects.get(user=new_user)
    exptected_data = {
      "token": token.key,
      "fullname": new_user.fullname,
      "email": new_user.email,
      "user_id": new_user.id
    }  
    self.assertEqual(response.data, exptected_data)

  def test_user_registration_400_fail_passwords_mismatch(self):
    """Ensure registration fails with a 400 error if passwords don't match."""
    url = reverse("registration")
    data = {
      "fullname": "Example Username",
      "email": "example@mail.com",
      "password": "examplePassword",
      "repeated_password": "examplePasswordsss"
    }

    response = self.client.post(url, data, format="json")

    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    self.assertEqual(response.data["password"], ["Passwords do not match."])

  def test_user_registration_400_fail_missing_fields(self):
    """Ensure registration fails with a 400 error if field is missing."""
    url = reverse("registration")
    data = {}

    response = self.client.post(url, data, format="json")

    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    self.assertIn("fullname", response.data)
    self.assertIn("email", response.data)
    self.assertIn("password", response.data)
    self.assertIn("repeated_password", response.data)

  def test_user_registration_400_fail_email_already_exists(self):
    """Ensure registration fails with a 400 error if the email already exists."""
    url = reverse("registration")
    User.objects.create_user(fullname="Duplicate Username", email="example@mail.com", password="12345")
    data = {
          "fullname": "Example Username",
          "email": "example@mail.com",
          "password": "examplePassword",
          "repeated_password": "examplePassword"
        }

    response = self.client.post(url, data, format="json") 

    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    self.assertEqual(response.data["email"], ["user with this email already exists."])

  def test_user_login_200_success(self):
    """
    Ensure user can successfully log in.

    Validates that the endpoint returns a 200 OK status code and that the response body
    contains the correct token and user details.
    """
    url = reverse("login")
    data = {"email": "setup-user@mail.com", "password": "setupPassword"}

    response = self.client.post(url, data, format="json")

    self.assertEqual(response.status_code, status.HTTP_200_OK)

    token = Token.objects.get(user=self.setup_user)
    expected_data = {
      "token": token.key,
      "fullname": self.setup_user.fullname,
      "email": self.setup_user.email,
      "user_id": self.setup_user.id
    }

    self.assertEqual(response.data, expected_data)

  def test_user_login_400_fail_wrong_password(self):
    """Ensure login fails with a 400 error if password ist wrong."""
    url = reverse("login")
    data = {"email": "setup-user@mail.com", "password": "ajdldjldjd"}

    response = self.client.post(url, data, format="json")

    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    self.assertIn("Invalid email or password.", response.data["non_field_errors"])

  def test_user_login_400_fail_user_does_not_exist(self):
    """Ensure login fails with a 400 error if user does not exist."""
    url = reverse("login")
    data = {"email": "user@mail.com", "password": "setupPassword"}

    response = self.client.post(url, data, format="json")

    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    self.assertIn("Invalid email or password.", response.data["non_field_errors"])

  def test_user_login_400_fail_missing_fields(self):
    """Ensure login fails with a 400 error if required fields are missing."""
    url = reverse("login")
    data = {}

    response = self.client.post(url, data, format="json")

    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    self.assertIn("email", response.data)
    self.assertIn("password", response.data)
    self.assertNotIn("token", response.data)


    
    






    



