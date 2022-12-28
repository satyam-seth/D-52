from data.models import Record, Water
from django.contrib import admin

# Register your models here.


@admin.register(Record)
class RecordAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "date", "item", "price", "datetime", "added_by")


@admin.register(Water)
class WaterAdmin(admin.ModelAdmin):
    list_display = ("id", "date", "quantity", "datetime", "added_by")
