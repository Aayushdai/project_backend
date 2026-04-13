#!/usr/bin/env python
"""Test the user preferences endpoint"""
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_companion.settings')
django.setup()

from django.contrib.auth.models import User
from apps.users.models import UserProfile
from rest_framework.test import APIRequestFactory, force_authenticate
from apps.users.views import user_preferences_view

# Get or create test user
user = User.objects.first()
if not user:
    print("✗ No users found in database")
    exit(1)

print(f"Testing preferences endpoint for user: {user.username}\n")

# Create a request factory
factory = APIRequestFactory()

# Test 1: GET preferences
print("Test 1: GET /users/me/preferences/")
request = factory.get('/users/me/preferences/')
force_authenticate(request, user=user)
response = user_preferences_view(request)
print(f"Status Code: {response.status_code}")
print(f"Response Data: {json.dumps(response.data, indent=2)}\n")

if response.status_code == 200:
    print("✓ GET request successful\n")
else:
    print("✗ GET request failed\n")

# Test 2: PATCH preferences (change some values)
print("Test 2: PATCH /users/me/preferences/")
patch_data = {
    "publicProfile": False,
    "showOnlineStatus": False,
    "emailNotifications": False,
}
request = factory.patch('/users/me/preferences/', patch_data, format='json')
force_authenticate(request, user=user)
response = user_preferences_view(request)
print(f"Status Code: {response.status_code}")
print(f"Response Data: {json.dumps(response.data, indent=2)}\n")

if response.status_code == 200:
    print("✓ PATCH request successful\n")
    
    # Verify changes persisted
    profile = user.userprofile
    print("Verifying changes in database:")
    print(f"  Public Profile: {profile.public_profile} (should be False)")
    print(f"  Show Online Status: {profile.show_online_status} (should be False)")
    print(f"  Email Notifications: {profile.email_notifications} (should be False)")
    
    if (not profile.public_profile and 
        not profile.show_online_status and 
        not profile.email_notifications):
        print("\n✓ All changes persisted correctly\n")
    else:
        print("\n✗ Some changes did not persist\n")
else:
    print("✗ PATCH request failed\n")

# Test 3: GET preferences again to verify updates
print("Test 3: GET /users/me/preferences/ (verify updates)")
request = factory.get('/users/me/preferences/')
force_authenticate(request, user=user)
response = user_preferences_view(request)
print(f"Status Code: {response.status_code}")
print(f"Response Data: {json.dumps(response.data, indent=2)}\n")

if response.status_code == 200:
    data = response.data
    if (not data['publicProfile'] and 
        not data['showOnlineStatus'] and 
        not data['emailNotifications']):
        print("✓ Updated preferences correctly returned in GET request\n")
    else:
        print("✗ Updated preferences not correctly returned\n")

print("=" * 50)
print("All preference endpoint tests completed!")
print("=" * 50)
