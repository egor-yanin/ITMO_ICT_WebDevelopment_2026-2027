from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy

from .forms import ConferenceReviewForm, TalkSubmissionForm
from .models import Conference, ConferenceReview, TalkSubmission


def _style_form(form):
    for field in form:
        classes = field.field.widget.attrs.get("class", "")
        field.field.widget.attrs["class"] = f"{classes} form-control".strip()
        if field.errors:
            field.field.widget.attrs["class"] += " is-invalid"


class StyledLoginView(LoginView):
    template_name = "app/login.html"
    redirect_authenticated_user = True

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        _style_form(form)
        return form


class RegistrationLogoutView(LogoutView):
    next_page = reverse_lazy("login")


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        _style_form(form)
        if form.is_valid():
            form.save()
            messages.success(request, "Регистрация прошла успешно. Теперь войдите в аккаунт.")
            return redirect("login")
    else:
        form = UserCreationForm()
        _style_form(form)

    return render(request, "app/register.html", {"form": form})


def conference_detail(request, conference_id):
    conference = get_object_or_404(
        Conference.objects.select_related("location").prefetch_related("themes"),
        pk=conference_id,
    )
    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect_to_login(
                request.get_full_path(),
                login_url=reverse_lazy("login"),
            )
        review_form = ConferenceReviewForm(request.POST)
        _style_form(review_form)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.conference = conference
            review.reviewer = request.user
            review.save()
            messages.success(request, "Ваш отзыв опубликован.")
            return redirect("conference_detail", conference_id=conference.pk)
    else:
        review_form = ConferenceReviewForm()
        _style_form(review_form)

    reviews = ConferenceReview.objects.filter(conference=conference).select_related(
        "reviewer"
    ).order_by("-created_at")
    recommended_submissions = (
        TalkSubmission.objects.filter(
            conference=conference,
            recommended_to_publish=True,
        )
        .select_related("author")
        .order_by("submitted_at")
    )
    return render(
        request,
        "app/conference_detail.html",
        {
            "conference": conference,
            "review_form": review_form,
            "reviews": reviews,
            "recommended_submissions": recommended_submissions,
        },
    )


@login_required(login_url="login")
def submit_talk(request, conference_id):
    conference = get_object_or_404(Conference, pk=conference_id)
    if request.method == "POST":
        form = TalkSubmissionForm(request.POST)
        _style_form(form)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.conference = conference
            submission.author = request.user
            submission.save()
            messages.success(request, "Заявка на выступление отправлена.")
            return redirect("conference_detail", conference_id=conference.pk)
    else:
        form = TalkSubmissionForm()
        _style_form(form)

    return render(
        request,
        "app/talk_submission_form.html",
        {"conference": conference, "form": form},
    )
