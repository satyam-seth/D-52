from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import CheckConstraint, Q

from accounts.models import Room, RoomMembership

# Create your models here.


class Record(models.Model):
    """Model to store purchase details"""

    class Meta:
        constraints = [
            CheckConstraint(
                check=Q(price__gte=0) & Q(price__lte=100000),
                name="price_non_negative_and_less_than_100000",
            )
        ]

    item = models.CharField(max_length=50)
    price = models.DecimalField(decimal_places=2, max_digits=9)
    purchaser = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="purchaser",
    )
    adder = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="adder",
    )
    room = models.ForeignKey(to=Room, on_delete=models.CASCADE, related_name="records")
    # TODO: Add validator for minimum date value is past 6 days and disallow future dates
    purchase_date = models.DateField()
    modified_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Ensure that purchaser and adder are members of the room
        purchaser_room_membership = RoomMembership.objects.filter(
            room=self.room,
            member=self.purchaser,
        )

        if not purchaser_room_membership.exists():
            raise ValidationError(
                message="Purchaser is from the same room as the record.",
                code="invalid_purchaser",
            )

        adder_room_membership = RoomMembership.objects.filter(
            room=self.room,
            member=self.adder,
        )

        if not adder_room_membership.exists():
            raise ValidationError(
                message="Adder is from the same room as the record.",
                code="invalid_adder",
            )

        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.item} {self.purchaser} {self.room.name}"


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
    """Model to store electricity bill details"""

    # TODO: add field to store bill and paid invoice image, and status paid or not
    # TODO: add paid_on date field
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
    """Model to store maid salary details"""

    # TODO: add paid_on date field
    due_date = models.DateField()
    price = models.DecimalField(
        decimal_places=2,
        max_digits=7,
    )
    modified_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return str(self.due_date)
