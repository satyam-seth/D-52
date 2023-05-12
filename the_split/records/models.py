from decimal import Decimal

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

# Create your models here.


class Record(models.Model):
    """Model to store purchase details"""

    item = models.CharField(max_length=50)
    # TODO: price can't be negative or zero
    price = models.DecimalField(
        decimal_places=2,
        max_digits=7,
        validators=[
            MinValueValidator(
                Decimal("0.01"),
            ),
        ],
    )
    # TODO: filter and allow only logged in user group users
    purchaser = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="purchaser",
    )
    adder = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="adder",
        null=True,
    )
    # TODO: Add validator for minimum date value is past 6 days and disallow future dates
    purchase_date = models.DateField()
    modified_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        # TODO: finalize str
        return f"{self.item} {self.purchaser.username}"


# TODO: Add price field because price of one gallon of water may change in future
class Water(models.Model):
    """Model to store water purchase details"""

    # currently we only allow maximum 5 quantity
    # TODO: add validator for allowed max quantity is 5 for a day
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[
            MaxValueValidator(5),
            MinValueValidator(1),
        ],
    )
    adder = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
    )
    purchase_date = models.DateField()
    modified_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        # TODO: finalize str
        return str(self.purchase_date)


# TODO: Create a common model to store electricity and maid data
# TODO: fix this model
class Electricity(models.Model):
    due_date = models.DateField()
    price = models.DecimalField(
        decimal_places=2,
        max_digits=7,
    )
    modified_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return str(self.due_date)


# TODO: fix this model
class Maid(models.Model):
    due_date = models.DateField()
    price = models.DecimalField(
        decimal_places=2,
        max_digits=7,
    )
    modified_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return str(self.due_date)
