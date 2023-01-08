from django import forms
from django.utils.timezone import localtime, now, timedelta

from .models import Record, Water


class RecordFrom(forms.ModelForm):
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
            # TODO: fix initial selected choice is current logged in user instead of ------
            "purchaser": forms.Select(attrs={"class": "form-control"}),
            "item": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter item name"}
            ),
            "price": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                    "max": "5000",
                    "placeholder": "Enter item price",
                }
            ),
        }


class WaterFrom(forms.ModelForm):
    class Meta:
        model = Water
        fields = ["purchase_date", "quantity"]
        widgets = {
            "purchase_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                    "min": localtime(now() - timedelta(20)).date(),
                    "max": localtime(now()).date(),
                    "value": localtime(now()).date(),
                }
            )
        }
