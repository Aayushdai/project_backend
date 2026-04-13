#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_companion.settings')
django.setup()

from apps.users.models import UserProfile
from apps.chat.models import Message

# Check a few users and their profile pictures
print("=== USER PROFILE PICTURES ===")
users = UserProfile.objects.all()[:5]
for user in users:
    pic = user.profile_picture
    print(f"User: {user.user.username}, Profile Pic: '{pic}', Bool: {bool(pic)}")

print("\n=== UNREAD MESSAGES ===")
messages = Message.objects.filter(is_read=False)[:5]
for msg in messages:
    sender = msg.sender
    if sender:
        pic = sender.profile_picture
        print(f"From {sender.user.username}: profile_picture='{pic}', Bool={bool(pic)}")
    else:
        print("Message with no sender")
