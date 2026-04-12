# Generated migration for expires_at field on TripInvitation

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trips', '0012_notification'),
    ]

    operations = [
        migrations.AddField(
            model_name='tripinvitation',
            name='expires_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
