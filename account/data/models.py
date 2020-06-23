from django.db import models

# Create your models here.

class Record(models.Model):
    date=models.DateField()
    datetime=models.DateTimeField()
    name=models.CharField(max_length=20)
    item=models.CharField(max_length=50)
    price=models.DecimalField(decimal_places=2,max_digits=5000)


    def __str__(self):
        return str(self.date)+' '+self.name

class Water(models.Model):
    date=models.DateField()
    datetime=models.DateTimeField()
    quantity=models.IntegerField()

    def __str__(self):
        return str(self.date)