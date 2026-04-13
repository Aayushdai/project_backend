#!/usr/bin/env python
"""Test preferences PATCH endpoint"""
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_companion.settings')
django.setup()

from django.contrib.auth.models import User
from rest_framework.test import APIRequestFactory, force_authenticate
from apps.users.views import user_preferences_view

print("Testing preferences endpoint...")

user = User.objects.first()
if not user:
    print("❌ No users found")
    exit(1)

profile = user.userprofile
factory = APIRequestFactory()

print(f"\nUser: {user.username}")
print(f"Current public_profile: {profile.public_profile}")

# Test PATCH with publicProfile set to False
print("\n" + "-" * 60)
print("Testing PATCH to turn OFF public_profile")
print("-" * 60)

data = {
    "publicProfile": False
}

request = factory.patch('/users/me/preferences/', data, format='json')
force_authenticate(request, user=user)

print(f"Sending: {json.dumps(data)}")
response = user_preferences_view(request)

print(f"Response Status: {response.status_code}")
print(f"Response Data: {json.dumps(response.data, indent=2)}")

# Verify in DB
profile.refresh_from_db()
print(f"\nDatabase check: public_profile = {profile.public_profile}")

if response.status_code == 200 and not profile.public_profile:
    print("✓ PATCH request successful and preference saved!")
else:
    print("❌ PATCH request failed")
    
# Test GET
print("\n" + "-" * 60)
print("Testing GET to verify saved value")
print("-" * 60)

request = factory.get('/users/me/preferences/')
force_authenticate(request, user=user)
response = user_preferences_view(request)

print(f"Response Status: {response.status_code}")
print(f"publicProfile in response: {response.data.get('publicProfile')}")

if response.data.get('publicProfile') == False:
    print("✓ GET returns correctly saved value!")
else:
    print("❌ GET does not return correct value")
