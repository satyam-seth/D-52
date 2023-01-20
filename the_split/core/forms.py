from core.models import Feedback
from django import forms


class FeedbackFrom(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ["name", "problem", "message"]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Your full name"}
            ),
            "problem": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Problem topic"}
            ),
            "message": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Suggetion message",
                    "rows": 5,
                }
            ),
        }
