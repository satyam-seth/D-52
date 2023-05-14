from typing import Any

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    AuthenticationForm,
    UserCreationForm,
    UsernameField,
)
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class LoginForm(AuthenticationForm):
    """Form to authentication user"""

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
    """Form for user signup"""

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
        }


class GroupJoinForm(forms.Form):
    group_name = forms.CharField(
        label="Group Name:",
        widget=forms.TextInput(attrs={"class": "form-control"}),
        help_text="Enter the group name to join",
    )

    def clean_group_name(self) -> Group:
        group_name = self.cleaned_data["group_name"]
        try:
            group = Group.objects.get(name=group_name)
        except Group.DoesNotExist:
            raise forms.ValidationError(
                _("group with name %(name)s is not found"),
                params={"name": group_name},
            )
        return group_name


class GroupCreateForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ("name",)
        labels = {"name": "Group Name:"}
        widgets = {"name": forms.TextInput(attrs={"class": "form-control"})}
