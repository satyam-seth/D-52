# Generated by Django 3.0.6 on 2023-01-09 18:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20230110_0017'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='cover_photo',
            field=models.ImageField(default='profile_cover_photos/default.jpg', upload_to='profile_cover_photo'),
        ),
    ]