# Generated by Django 3.0.6 on 2020-06-20 09:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Electricity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('due_date', models.DateField()),
                ('price', models.IntegerField()),
                ('datetime', models.DateTimeField()),
            ],
        ),
    ]
