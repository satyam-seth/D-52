from typing import Any

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.forms import (
    AuthenticationForm,
    UserCreationForm,
    UsernameField,
)
from django.utils.translation import gettext_lazy as _

User = get_user_model()


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


class SignUpForm(UserCreationForm):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields["password1"].widget.attrs["class"] = "form-control"
        self.fields["password2"].widget.attrs["class"] = "form-control"

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "password1",
            "password2",
        ]

        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "password1": forms.PasswordInput(attrs={"class": "form-control"}),
            "password2": forms.PasswordInput(attrs={"class": "form-control"}),
        }


class GroupJoinForm(forms.Form):
    group_name = forms.CharField(
        label="Group Name:",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )


class GroupCreateForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ("name",)
        labels = {"name": "Group Name:"}
        widgets = {"name": forms.TextInput(attrs={"class": "form-control"})}
