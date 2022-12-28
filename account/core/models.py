from django.db import models

# Create your models here.


class Feedback(models.Model):
    name = models.CharField(max_length=20)
    problem = models.CharField(max_length=100)
    message = models.TextField(max_length=500)
    datetime = models.DateTimeField()

    def __str__(self):
        return self.problem


class Electricity(models.Model):
    due_date = models.DateField()
    price = models.DecimalField(decimal_places=2, max_digits=7)
    datetime = models.DateTimeField()

    def __str__(self):
        return str(self.due_date)


class Maid(models.Model):
    due_date = models.DateField()
    price = models.DecimalField(decimal_places=2, max_digits=7)
    datetime = models.DateTimeField()

    def __str__(self):
        return str(self.due_date)
