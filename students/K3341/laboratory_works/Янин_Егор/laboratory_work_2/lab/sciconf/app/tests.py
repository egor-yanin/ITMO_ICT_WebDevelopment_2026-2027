from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Conference, ConferenceReview, Location, Theme


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


class ConferenceDetailViewTests(TestCase):
    def setUp(self):
        self.location = Location.objects.create(
            name="Университет",
            address="Санкт-Петербург",
            description="Главный корпус",
        )
        self.theme = Theme.objects.create(
            name="Информационные технологии",
            description="Исследования в области ИТ",
        )
        self.conference = Conference.objects.create(
            name="SciConf 2026",
            location=self.location,
            start_date="2026-11-10",
            end_date="2026-11-12",
            participation_terms="Подать тезисы до 1 ноября",
        )
        self.conference.themes.add(self.theme)

    def test_existing_conference_is_displayed(self):
        response = self.client.get(
            reverse("conference_detail", args=[self.conference.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.conference.name)
        self.assertContains(response, self.location.name)
        self.assertContains(response, self.theme.name)
        self.assertContains(response, self.conference.participation_terms)

    def test_missing_conference_returns_404(self):
        response = self.client.get(reverse("conference_detail", args=[99999]))

        self.assertEqual(response.status_code, 404)

    def test_anonymous_user_is_redirected_to_login_to_post_review(self):
        response = self.client.post(
            reverse("conference_detail", args=[self.conference.pk]),
            {"review_text": "Отличная конференция", "rating": 9},
        )

        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('conference_detail', args=[self.conference.pk])}",
        )
        self.assertFalse(ConferenceReview.objects.exists())

    def test_authenticated_user_can_post_review(self):
        reviewer = get_user_model().objects.create_user(
            username="conference_reviewer",
            password="Strong-test-password-739!",
        )
        self.client.force_login(reviewer)

        response = self.client.post(
            reverse("conference_detail", args=[self.conference.pk]),
            {"review_text": "Хорошая программа и организация.", "rating": 9},
        )

        self.assertRedirects(
            response,
            reverse("conference_detail", args=[self.conference.pk]),
        )
        review = ConferenceReview.objects.get()
        self.assertEqual(review.conference, self.conference)
        self.assertEqual(review.reviewer, reviewer)
        self.assertEqual(review.rating, 9)

    def test_rating_out_of_range_does_not_create_review(self):
        reviewer = get_user_model().objects.create_user(
            username="conference_reviewer",
            password="Strong-test-password-739!",
        )
        self.client.force_login(reviewer)

        response = self.client.post(
            reverse("conference_detail", args=[self.conference.pk]),
            {"review_text": "Текст отзыва", "rating": 11},
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(ConferenceReview.objects.exists())

    def test_existing_reviews_are_displayed(self):
        reviewer = get_user_model().objects.create_user(
            username="conference_reviewer",
            password="Strong-test-password-739!",
        )
        ConferenceReview.objects.create(
            conference=self.conference,
            reviewer=reviewer,
            review_text="Полезное мероприятие.",
            rating=8,
        )
        self.client.force_login(reviewer)

        response = self.client.get(
            reverse("conference_detail", args=[self.conference.pk])
        )

        self.assertContains(response, "Полезное мероприятие.")
        self.assertContains(response, "conference_reviewer")
