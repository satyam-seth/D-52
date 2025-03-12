from datetime import timedelta

from django import forms
from django.contrib.auth import get_user_model
from django.utils.timezone import localtime, now

from records.models import Record, Water

User = get_user_model()


class RecordForm(forms.ModelForm):
    """Form for item purchase"""

    def __init__(self, *args, **kwargs):
        self.now = localtime(now())
        self.room_id = kwargs.pop("room_id", None)
        super().__init__(*args, **kwargs)

        if self.room_id:
            room_members = User.objects.filter(room_membership__room_id=self.room_id)
            self.fields["purchaser"].queryset = room_members

        self.fields["purchase_datetime"].widget.attrs.update(
            {
                "min": (
                    self.now - timedelta(days=Record.max_allowed_past_days)
                ).strftime("%Y-%m-%dT%H:%M"),
                "max": self.now.strftime("%Y-%m-%dT%H:%M"),
                "value": self.now.strftime("%Y-%m-%dT%H:%M"),
            }
        )

    class Meta:
        model = Record
        fields = ["purchase_datetime", "purchaser", "item", "price"]
        widgets = {
            "purchase_datetime": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local",
                    "class": "form-control",
                }
            ),
            "purchaser": forms.Select(attrs={"class": "form-control"}),
            "item": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter item name"}
            ),
            "price": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                    "max": "100000",
                    "placeholder": "Enter item price",
                }
            ),
        }


class WaterForm(forms.ModelForm):
    """Form for water purchase"""

    def __init__(self, *args, **kwargs):
        self.now = localtime(now())
        super().__init__(*args, **kwargs)

        self.fields["purchase_datetime"].widget.attrs.update(
            {
                "min": (
                    self.now - timedelta(days=Water.max_allowed_past_days)
                ).strftime("%Y-%m-%dT%H:%M"),
                "max": self.now.strftime("%Y-%m-%dT%H:%M"),
                "value": self.now.strftime("%Y-%m-%dT%H:%M"),
            }
        )

    class Meta:
        model = Water
        fields = ["purchase_datetime", "quantity"]
        widgets = {
            "purchase_datetime": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local",
                    "class": "form-control",
                }
            ),
            "quantity": forms.NumberInput(
                # TODO: fix it min value still 0 in html input tag
                # and it can be inhabited from model field validator
                attrs={
                    "class": "form-control",
                    "min": 1,
                    "max": model.max_allowed_quality,
                }
            ),
        }
