# Generated by Django 5.1.5 on 2025-02-15 23:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_notification_nba'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='profile_photo',
            field=models.ImageField(default='images/default_images/default_profile_photo.svg', upload_to='images/users/profile_photo/%Y/%m/%d', verbose_name='프로필 사진'),
        ),
    ]
