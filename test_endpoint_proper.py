#!/usr/bin/env python
"""Test the chat endpoint with proper HTTP request setup"""
import os
import sys
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_companion.settings')
django.setup()

from django.contrib.auth.models import User
from apps.users.models import UserProfile
from rest_framework_simplejwt.tokens import RefreshToken
from django.test import Client

print("=" * 80)
print("TESTING CHAT ENDPOINT WITH PROPER HOST")
print("=" * 80)

# Create test user
user, created = User.objects.get_or_create(
    username='testchatuser',
    defaults={'email': 'chat@test.com'}
)
print(f"[OK] User: {user.username}")

# Create user profile
profile, _ = UserProfile.objects.get_or_create(
    user=user,
    defaults={'bio': 'Test user'}
)
print(f"[OK] UserProfile exists")

# Get JWT token
refresh = RefreshToken.for_user(user)
access_token = str(refresh.access_token)
print(f"[OK] JWT Token generated: {access_token[:30]}...")

# Create client with proper SERVER_NAME
client = Client(SERVER_NAME='127.0.0.1')

# Test 1: Test with message
print("\n[TEST 1] Sending 'hello' message...")
try:
    response = client.post(
        '/api/chat/chat/',
        data=json.dumps({'message': 'hello'}),
        content_type='application/json',
        HTTP_AUTHORIZATION=f'Bearer {access_token}'
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        data = json.loads(response.content)
        print(f"[OK] Response: {json.dumps(data, indent=2)[:300]}...")
    else:
        print(f"[ERROR] Response: {response.content.decode()[:500]}")
except Exception as e:
    print(f"[ERROR] Exception: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Test with map query
print("\n[TEST 2] Sending 'show map' message...")
try:
    response = client.post(
        '/api/chat/chat/',
        data=json.dumps({'message': 'show map'}),
        content_type='application/json',
        HTTP_AUTHORIZATION=f'Bearer {access_token}'
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        data = json.loads(response.content)
        print(f"[OK] Response received")
    else:
        print(f"[ERROR] Response: {response.content.decode()[:500]}")
except Exception as e:
    print(f"[ERROR] Exception: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("TESTS COMPLETE")
print("=" * 80)
