from django.contrib.auth.models import User
from django.test import TestCase
from ninja.testing.client import TestClient

from .routes import router


class UserAPITestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        username = "testuser"
        password = "#StrongPass1"
        cls.username = username
        cls.password = password
        cls.user = User.objects.create_user(
            username=username,
            password=password,
        )
        cls.client = TestClient(router_or_app=router)
        cls.register_url = "/api/users/register"
        cls.login_url = "/api/token/pair"

    def test_register_user_success(self):
        response = self.client.post(
            self.register_url,
            data={
                "username": "newuser",
                "password": "#NewStrongPass1",
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "OK"})

    def test_register_user_already_exists(self):
        response = self.client.post(
            self.register_url,
            {"username": self.username, "password": "#AnotherStrongPass1"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        json_response = response.json()
        self.assertIn("detail", json_response)
        self.assertEqual(json_response["detail"], "Username already taken")

    def test_login_user_success(self):
        response = self.client.post(
            self.login_url,
            {"username": self.username, "password": self.password},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)

        json_response = response.json()
        self.assertIn("access", json_response)
        self.assertIn("refresh", json_response)

    def test_login_invalid_password(self):
        response = self.client.post(
            self.login_url,
            {"username": self.username, "password": "wrongpassword"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 401)
        json_response = response.json()
        self.assertIn("detail", json_response)
        self.assertEqual(json_response["detail"], "No active account found with the given credentials")

    def test_login_invalid_username(self):
        response = self.client.post(
            self.login_url,
            {"username": "wronguser", "password": self.password},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 401)
        json_response = response.json()
        self.assertIn("detail", json_response)
        self.assertEqual(json_response["detail"], "No active account found with the given credentials")
