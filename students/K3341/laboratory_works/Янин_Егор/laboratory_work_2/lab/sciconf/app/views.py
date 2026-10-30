from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render


def _style_registration_form(form):
    for field in form:
        classes = field.field.widget.attrs.get("class", "")
        field.field.widget.attrs["class"] = f"{classes} form-control".strip()
        if field.errors:
            field.field.widget.attrs["class"] += " is-invalid"


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        _style_registration_form(form)
        if form.is_valid():
            form.save()
            messages.success(request, "Регистрация прошла успешно.")
            return redirect("register")
    else:
        form = UserCreationForm()
        _style_registration_form(form)

    return render(request, "app/register.html", {"form": form})
