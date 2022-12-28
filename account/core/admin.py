from core.models import Electricity, Feedback, Maid
from django.contrib import admin

# Register your models here.


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "problem", "message", "datetime")


@admin.register(Electricity)
class ElectricityAdmin(admin.ModelAdmin):
    list_display = ("id", "due_date", "price", "datetime")


@admin.register(Maid)
class MaidAdmin(admin.ModelAdmin):
    list_display = ("id", "due_date", "price", "datetime")
