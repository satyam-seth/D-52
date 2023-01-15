from core.models import Electricity, Feedback, Maid, Profile
from django.contrib import admin


# TODO: register profile under user model
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "avatar")


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "problem", "message", "datetime")


@admin.register(Electricity)
class ElectricityAdmin(admin.ModelAdmin):
    list_display = ("id", "due_date", "price", "datetime")


@admin.register(Maid)
class MaidAdmin(admin.ModelAdmin):
    list_display = ("id", "due_date", "price", "datetime")
