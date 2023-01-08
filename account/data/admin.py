from data.models import Record, Water
from django.contrib import admin

# Register your models here.


@admin.register(Record)
class RecordAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "item",
        "price",
        "purchaser",
        "adder",
        "purchase_date",
        "created_on",
        "modified_on",
    )


@admin.register(Water)
class WaterAdmin(admin.ModelAdmin):
    list_display = ("id", "date", "quantity", "datetime", "added_by")
