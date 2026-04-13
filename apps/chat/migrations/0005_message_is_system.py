# Generated migration for adding is_system field to Message model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0004_alter_message_options_alter_message_receiver'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='is_system',
            field=models.BooleanField(default=False, help_text='System message (e.g., user joined/left)'),
        ),
    ]
