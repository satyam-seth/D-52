from core.models import Feedback
from django.contrib import admin

# Register your models here.


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "problem",
        "message",
        "datetime",
    )
