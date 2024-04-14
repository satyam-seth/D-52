from typing import Any

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    AuthenticationForm,
    UserCreationForm,
    UsernameField,
)
from django.utils.translation import gettext_lazy as _

from accounts.models import Profile, Room

User = get_user_model()


class ProfileUpdateForm(forms.ModelForm):
    """Form to update user profile"""

    class Meta:
        model = Profile
        fields = ["avatar", "cover_photo"]


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


# class RoomJoinForm(forms.Form):
#     """Form to join a room"""

#     room_id = forms.IntegerField(
#         label="Room ID:",
#         widget=forms.TextInput(attrs={"class": "form-control"}),
#         help_text="Enter the room id to join",
#     )

#     def clean_room_id(self) -> Group:
#         """Clean and validate the room id field"""

#         room_id = self.cleaned_data["room_id"]

#         # TODO: make sure user can join the room if already invited for room
#         try:
#             Room.objects.get(id=room_id)
#         except Room.DoesNotExist as exc:
#             raise forms.ValidationError(
#                 _("room with id %(room_id)d is not found"),
#                 params={"room_id": room_id},
#             ) from exc

#         return room_id


class RoomCreateForm(forms.ModelForm):
    """Form to create a Room"""

    class Meta:
        model = Room
        fields = ("name",)
        labels = {"name": "Room Name:"}
        widgets = {"name": forms.TextInput(attrs={"class": "form-control"})}
