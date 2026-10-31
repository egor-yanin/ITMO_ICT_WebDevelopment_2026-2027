from django.urls import path

from . import views

urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.StyledLoginView.as_view(), name="login"),
    path("logout/", views.RegistrationLogoutView.as_view(), name="logout"),
]
