# Generated by Django 5.1.5 on 2025-02-06 06:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diaries', '0005_frame_image_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='diary',
            name='address',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='주소'),
        ),
    ]
