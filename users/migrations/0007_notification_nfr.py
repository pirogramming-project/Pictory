# Generated by Django 5.1.5 on 2025-02-07 15:32

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_notification_tag'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification_NFR',
            fields=[
                ('notification', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='nfr_notification', serialize=False, to='users.notification')),
                ('from_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='related_notifications', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
