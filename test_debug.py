#!/usr/bin/env python
import os
import sys
import django
import traceback

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_companion.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from apps.users.models import UserProfile
from rest_framework_simplejwt.tokens import RefreshToken
import json

print("=" * 60)
print("TESTING CHAT ENDPOINT")
print("=" * 60)

# Create test user
user, _ = User.objects.get_or_create(
    username='debuguser',
    defaults={'email': 'debug@test.com'}
)
print(f"✓ User: {user.username}")

# Create user profile
profile, _ = UserProfile.objects.get_or_create(
    user=user,
    defaults={'bio': 'Debug user'}
)
print(f"✓ UserProfile: created")

# Get token
refresh = RefreshToken.for_user(user)
access_token = str(refresh.access_token)
print(f"✓ Token generated")

# Create Django test client
client = Client()
print(f"✓ Test client created")

# Make request
try:
    response = client.post(
        '/api/chat/chat/',
        data=json.dumps({'message': 'hello'}),
        content_type='application/json',
        HTTP_AUTHORIZATION=f'Bearer {access_token}'
    )
    print(f"\n✓ Request succeeded with status: {response.status_code}")
    print(f"Response content: {response.content.decode()[:500]}")
except Exception as e:
    print(f"\n✗ Request failed with error:")
    traceback.print_exc()
