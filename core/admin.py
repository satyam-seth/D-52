from django.contrib import admin

from core.models import Feedback

# Register your models here.


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    """Admin configuration for the Feedback model."""

    list_display = (
        "id",
        "name",
        "problem",
        "message",
        "datetime",
    )
