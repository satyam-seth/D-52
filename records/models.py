from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from accounts.models import Room, RoomMembership
from records.validators import validate_past_datetime_within_past_6_days

# Create your models here.


class BasePurchaseModel(models.Model):
    """Abstract base model to handle purchase datetime logic"""

    max_allowed_past_days = 6

    class Meta:
        abstract = True

    purchase_datetime = models.DateTimeField(
        validators=[validate_past_datetime_within_past_6_days]
    )

    def save(self, *args, **kwargs):
        # Ensure purchase_datetime is timezone-aware
        if timezone.is_naive(self.purchase_datetime):
            # If it's naive, assume it's in the local timezone
            self.purchase_datetime = timezone.make_aware(
                self.purchase_datetime, timezone.get_current_timezone()
            )

        # Ensure that the purchase date is within the last six days
        now_utc = timezone.now()
        min_past_datetime_utc = now_utc - timedelta(days=self.max_allowed_past_days)
        purchase_datetime_utc = self.purchase_datetime.astimezone(timezone.utc)

        if (
            purchase_datetime_utc > now_utc
            or purchase_datetime_utc < min_past_datetime_utc
        ):
            raise ValidationError(
                message="Purchase datetime should be within the past "
                + f"{self.max_allowed_past_days} days.",
                code="invalid_purchase_datetime",
            )

        super().save(*args, **kwargs)


class Record(BasePurchaseModel):
    """Model to store purchase details"""

    max_allowed_past_days = 6

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(price__gte=0) & models.Q(price__lte=100000),
                name="price_non_negative_and_less_than_100000",
            )
        ]

    item = models.CharField(max_length=50)
    price = models.DecimalField(
        decimal_places=2,
        max_digits=9,
        validators=[
            MinValueValidator(Decimal("0")),
            MaxValueValidator(Decimal("100000")),
        ],
    )
    purchaser = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="purchaser",
    )
    adder = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="record_adder",
    )
    room = models.ForeignKey(to=Room, on_delete=models.CASCADE, related_name="records")
    modified_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Ensure that purchaser is members of the room
        purchaser_room_membership = RoomMembership.objects.filter(
            room=self.room,
            member=self.purchaser,
        )

        if not purchaser_room_membership.exists():
            raise ValidationError(
                message="Purchaser is from the same room as the record.",
                code="invalid_purchaser",
            )

        # Ensure that adder is members of the room
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
        return f"{self.item} {self.purchaser} {self.purchase_datetime} {self.room.name}"


# TODO: Add price field because price of one gallon of water may change in future
class Water(BasePurchaseModel):
    """Model to store water purchase details"""

    max_allowed_quality = 5

    quantity = models.PositiveIntegerField(
        default=1,
        validators=[
            MaxValueValidator(max_allowed_quality),
            MinValueValidator(1),
        ],
    )
    adder = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="water_adder",
    )
    room = models.ForeignKey(to=Room, on_delete=models.CASCADE, related_name="waters")
    modified_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Ensure that maximum `max_allowed_quality` quantity allowed per day
        total_water_quantity = self.quantity

        if total_water_quantity <= self.max_allowed_quality:
            water_entires = Water.objects.filter(
                room=self.room,
                purchase_datetime=self.purchase_datetime,
            )

            if water_entires.count() > 0:
                stored_water_quantity = water_entires.aggregate(
                    stored_quantity=models.Sum("quantity")
                )["stored_quantity"]
                total_water_quantity += stored_water_quantity

        if total_water_quantity > self.max_allowed_quality:
            raise ValidationError(
                f"Maximum {self.max_allowed_quality} water quantity allowed per day.",
                code="exceeds_max_quantity",
            )

        # Ensure that adder is members of the room
        adder_room_membership = RoomMembership.objects.filter(
            room=self.room,
            member=self.adder,
        )

        if not adder_room_membership.exists():
            raise ValidationError(
                message="Adder is from the same room as the water.",
                code="invalid_adder",
            )

        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.purchase_datetime} {self.room.name}"


# TODO: Add room info
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


# TODO: Add room info
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
