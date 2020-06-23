from django.contrib import admin
from core.models import Feedback,Electricity,Maid

# Register your models here.

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display=('id','name','problem','message','datetime')

@admin.register(Electricity)
class ElectricityAdmin(admin.ModelAdmin):
    list_display=('id','due_date','price','datetime')

@admin.register(Maid)
class MaidAdmin(admin.ModelAdmin):
    list_display=('id','due_date','price','datetime')