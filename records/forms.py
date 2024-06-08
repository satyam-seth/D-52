from datetime import timedelta

from django import forms
from django.contrib.auth import get_user_model
from django.utils.timezone import localtime, now

from records.models import Record, Water

User = get_user_model()


class RecordForm(forms.ModelForm):
    """Form for item purchase"""

    def __init__(self, *args, **kwargs):
        self.room_id = kwargs.pop("room_id", None)
        super().__init__(*args, **kwargs)
        if self.room_id:
            room_members = User.objects.filter(room_membership__room__id=self.room_id)
            self.fields["purchaser"].queryset = room_members

    class Meta:
        model = Record
        fields = ["purchase_date", "purchaser", "item", "price"]
        widgets = {
            "purchase_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                    # TODO: move this validator logic to models
                    "min": localtime(now() - timedelta(6)).date(),
                    "max": localtime(now()).date(),
                    "value": localtime(now()).date(),
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

    class Meta:
        model = Water
        fields = ["purchase_date", "quantity"]
        widgets = {
            # TODO: find out right way to infer max value from model validators if possible
            "purchase_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                    "min": localtime(now() - timedelta(20)).date(),
                    "max": localtime(now()).date(),
                    "value": localtime(now()).date(),
                }
            ),
            "quantity": forms.NumberInput(
                # TODO: fix it min value still 0 in html input tag
                # and it can be inhabited from model field validator
                attrs={
                    "class": "form-control",
                    "min": 1,
                    "max": 5,
                }
            ),
        }
