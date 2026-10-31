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

        self.assertRedirects(response, reverse("register"))
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
