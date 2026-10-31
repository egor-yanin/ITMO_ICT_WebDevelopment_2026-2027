from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class RegistrationViewTests(TestCase):
    def test_registration_page_is_displayed(self):
        response = self.client.get(reverse("register"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Зарегистрироваться")

    def test_valid_registration_creates_user(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "conference_author",
                "password1": "Strong-test-password-739!",
                "password2": "Strong-test-password-739!",
            },
        )

        self.assertRedirects(response, reverse("login"))
        user = get_user_model().objects.get(username="conference_author")
        self.assertTrue(user.check_password("Strong-test-password-739!"))

    def test_invalid_registration_does_not_create_user(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "conference_author",
                "password1": "Strong-test-password-739!",
                "password2": "Different-password-739!",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            get_user_model().objects.filter(username="conference_author").exists()
        )


class AuthenticationViewTests(TestCase):
    def setUp(self):
        self.password = "Strong-test-password-739!"
        self.user = get_user_model().objects.create_user(
            username="conference_author",
            password=self.password,
        )

    def test_login_page_is_displayed(self):
        response = self.client.get(reverse("login"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Войти")

    def test_valid_credentials_log_user_in(self):
        response = self.client.post(
            reverse("login"),
            {"username": self.user.username, "password": self.password},
        )

        self.assertRedirects(response, reverse("register"))
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_invalid_credentials_do_not_log_user_in(self):
        response = self.client.post(
            reverse("login"),
            {"username": self.user.username, "password": "wrong-password"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_logout_ends_session(self):
        self.client.force_login(self.user)

        response = self.client.post(reverse("logout"))

        self.assertRedirects(response, reverse("login"))
        self.assertNotIn("_auth_user_id", self.client.session)
