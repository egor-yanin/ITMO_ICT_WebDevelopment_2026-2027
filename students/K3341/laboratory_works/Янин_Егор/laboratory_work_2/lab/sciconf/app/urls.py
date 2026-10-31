from django.urls import path

from . import views

urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.StyledLoginView.as_view(), name="login"),
    path("logout/", views.RegistrationLogoutView.as_view(), name="logout"),
    path("conferences/<int:conference_id>/", views.conference_detail, name="conference_detail"),
    path("conferences/<int:conference_id>/submit/", views.submit_talk, name="submit_talk"),
]
