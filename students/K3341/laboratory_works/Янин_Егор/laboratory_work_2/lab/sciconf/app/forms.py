from django import forms

from .models import ConferenceReview


class ConferenceReviewForm(forms.ModelForm):
    class Meta:
        model = ConferenceReview
        fields = ("review_text", "rating")
        widgets = {
            "review_text": forms.Textarea(
                attrs={"rows": 4, "placeholder": "Поделитесь впечатлениями"}
            ),
            "rating": forms.NumberInput(attrs={"min": 1, "max": 10}),
        }
