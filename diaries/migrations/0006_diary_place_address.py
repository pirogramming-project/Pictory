# Generated by Django 5.1.5 on 2025-02-06 07:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diaries', '0005_frame_image_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='diary',
            name='place_address',
            field=models.CharField(default='서울시', max_length=120, verbose_name='실주소'),
            preserve_default=False,
        ),
    ]
