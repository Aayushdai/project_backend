#!/usr/bin/env python
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_companion.settings')
django.setup()

from apps.users.models import UserProfile
from apps.chat.models import Message
from apps.chat.views import MessageSerializer

# Get an unread message
msg = Message.objects.filter(is_read=False).first()

if msg:
    # Serialize it
    serializer = MessageSerializer(msg)
    data = serializer.data
    
    print("=== MESSAGE SERIALIZER OUTPUT ===")
    print(json.dumps(data, indent=2, default=str))
    print(f"\nprofile_picture field value: '{data.get('profile_picture')}'")
else:
    print("No unread messages found")
