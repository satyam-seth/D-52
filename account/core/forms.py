from django import forms
from django.contrib.auth.forms import AuthenticationForm, UsernameField
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _

from .models import Feedback


class LoginForm(AuthenticationForm):
    username = UsernameField(
        widget=forms.TextInput(attrs={"autofocus": True, "class": "form-control"})
    )
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={"autocomplete": "current-password", "class": "form-control"}
        ),
    )


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
