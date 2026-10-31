from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy

from .forms import ConferenceReviewForm
from .models import Conference, ConferenceReview


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
    return render(
        request,
        "app/conference_detail.html",
        {
            "conference": conference,
            "review_form": review_form,
            "reviews": reviews,
        },
    )
