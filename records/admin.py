from django.contrib import admin

from records.models import Electricity, Maid, Record, Water

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
    list_display = (
        "id",
        "quantity",
        "adder",
        "purchase_date",
        "created_on",
        "modified_on",
    )


@admin.register(Electricity)
class ElectricityAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "due_date",
        "price",
        "created_on",
        "modified_on",
    )


@admin.register(Maid)
class MaidAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "due_date",
        "price",
        "created_on",
        "modified_on",
    )
