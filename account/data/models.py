from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Record(models.Model):
    item = models.CharField(max_length=50)
    price = models.DecimalField(decimal_places=2, max_digits=7)
    purchaser = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="purchaser"
    )
    adder = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name="adder", null=True
    )
    purchase_date = models.DateField()
    modified_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.item) + " " + self.purchaser.username


class Water(models.Model):
    date = models.DateField()
    datetime = models.DateTimeField()
    quantity = models.IntegerField()
    added_by = models.CharField(max_length=50)

    def __str__(self):
        return str(self.date)
