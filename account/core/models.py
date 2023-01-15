from django.conf import settings
from django.db import models


# TODO: move this model in accounts app
class Profile(models.Model):
    user = models.OneToOneField(
        to=settings.AUTH_USER_MODEL, related_name="profile", on_delete=models.CASCADE
    )
    # TODO: add default images
    avatar = models.ImageField(
        default="profile_images/default.jpg", upload_to="profile_images"
    )
    cover_photo = models.ImageField(
        default="profile_cover_photos/default.jpg", upload_to="profile_cover_photo"
    )

    def __str__(self) -> str:
        return self.user.username


class Feedback(models.Model):
    # TODO: remove name field
    name = models.CharField(max_length=20)
    # TODO: make choice field with predefined and other as custom problem field
    problem = models.CharField(max_length=100)
    message = models.TextField(max_length=500)
    datetime = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.problem


class Electricity(models.Model):
    due_date = models.DateField()
    price = models.DecimalField(decimal_places=2, max_digits=7)
    datetime = models.DateTimeField()

    def __str__(self) -> str:
        return str(self.due_date)


class Maid(models.Model):
    due_date = models.DateField()
    price = models.DecimalField(decimal_places=2, max_digits=7)
    datetime = models.DateTimeField()

    def __str__(self) -> str:
        return str(self.due_date)
