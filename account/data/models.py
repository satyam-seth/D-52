from django.db import models

# Create your models here.


class Record(models.Model):
    date = models.DateField()
    datetime = models.DateTimeField()
    name = models.CharField(max_length=20)
    item = models.CharField(max_length=50)
    price = models.DecimalField(decimal_places=2, max_digits=7)
    added_by = models.CharField(max_length=50)

    def __str__(self):
        return str(self.date) + " " + self.name


class Water(models.Model):
    date = models.DateField()
    datetime = models.DateTimeField()
    quantity = models.IntegerField()
    added_by = models.CharField(max_length=50)

    def __str__(self):
        return str(self.date)
