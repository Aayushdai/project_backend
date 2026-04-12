# Generated migration for Notification model
# This migration creates the trips_notification table

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('trips', '0011_tripinvitelink_tripinvitation'),
        ('users', '0007_remove_userprofile_rejection_reason_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notification_type', models.CharField(choices=[('invitation_received', 'Invitation Received'), ('invitation_accepted', 'Invitation Accepted'), ('invitation_rejected', 'Invitation Rejected'), ('member_joined', 'Member Joined'), ('member_left', 'Member Left'), ('trip_updated', 'Trip Updated')], max_length=30)),
                ('message', models.TextField()),
                ('is_read', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('actor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='notifications_sent', to='users.userprofile')),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications_received', to='users.userprofile')),
                ('trip', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='trips.trip')),
                ('invitation', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='trips.tripinvitation')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
