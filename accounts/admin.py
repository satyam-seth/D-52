from django.contrib import admin

from accounts.models import Profile

# Register your models here.


# TODO: register profile under user model as inline
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "avatar",
        "cover_photo",
    )
