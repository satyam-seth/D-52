# Generated by Django 3.0.6 on 2020-06-21 23:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='record',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=5000),
        ),
    ]
