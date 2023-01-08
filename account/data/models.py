from decimal import Decimal

from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models

# Create your models here.


class Record(models.Model):
    item = models.CharField(max_length=50)
    # TODO: price can't be negative or zero
    price = models.DecimalField(
        decimal_places=2, max_digits=7, validators=[MinValueValidator(Decimal("0.01"))]
    )
    # TODO: filter and allow only logged in user group users
    purchaser = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="purchaser"
    )
    adder = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name="adder", null=True
    )
    # TODO: Add validator for minimum date value is past 6 days and disallow future dates
    purchase_date = models.DateField()
    modified_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # TODO: finalize str
        return str(self.item) + " " + self.purchaser.username


class Water(models.Model):
    purchase_date = models.DateField()
    modified_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)
    quantity = models.PositiveIntegerField()
    adder = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        # TODO: finalize str
        return str(self.purchase_date)
