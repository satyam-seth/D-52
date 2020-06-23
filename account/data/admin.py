from django.contrib import admin
from data.models import Record,Water

# Register your models here.

@admin.register(Record)
class RecordAdmin(admin.ModelAdmin):
    list_display=('id','name','date','item','price','datetime')

@admin.register(Water)
class WaterAdmin(admin.ModelAdmin):
    list_display=('id','date','quantity','datetime')