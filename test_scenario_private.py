#!/usr/bin/env python
"""Test private profile visibility simulation"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_companion.settings')
django.setup()

from django.contrib.auth.models import User
from django.db.models import Q
from apps.users.models import UserProfile, FriendRequest
from rest_framework.test import APIRequestFactory, force_authenticate
from apps.users.views_api import get_user_profile, search_users

print("=" * 70)
print("SIMULATE USER SCENARIO: TURN OFF PUBLIC PROFILE & VIEW REMAINS HIDDEN")
print("=" * 70)

# Get test users - ishan and another viewer
users_list = list(User.objects.all()[:2])
if len(users_list) < 2:
    print("❌ Need at least 2 users")
    exit(1)

ishan = users_list[0]  # Profile owner
other_user = users_list[1]  # Trying to view

ishan_profile = ishan.userprofile
other_profile = other_user.userprofile

print(f"\nSetup:")
print(f"  • Ishan (profile owner): {ishan.username}")
print(f"  • Other user (viewer): {other_user.username}")

# Clear any existing friendships
FriendRequest.objects.filter(
    Q(from_user=ishan, to_user=other_user) | Q(from_user=other_user, to_user=ishan)
).delete()

factory = APIRequestFactory()

# STEP 1: Ishan sets profile to PRIVATE
print("\n" + "-" * 70)
print("STEP 1: Ishan turns OFF 'Public Profile'")
print("-" * 70)

ishan_profile.public_profile = False
ishan_profile.travel_style = "Adventure"  # Ensure has some preference data
ishan_profile.pace = "Moderate"
ishan_profile.accomodation_preference = "Camping"
ishan_profile.save()
print(f"✓ Ishan's public_profile is now: {ishan_profile.public_profile}")

# STEP 2: Other user tries to view ishan's profile directly  
print("\n" + "-" * 70)
print("STEP 2: Other user tries to view ishan's profile (direct access)")
print("-" * 70)

request = factory.get(f'/api/users/user-profile/{ishan.id}/')
force_authenticate(request, user=other_user)
response = get_user_profile(request, ishan.id)

print(f"Request: GET /api/users/user-profile/{ishan.id}/")
print(f"Response Status: {response.status_code}")
if response.status_code == 403:
    print(f"✓ BLOCKED correctly! Private profile access denied")
    print(f"  Message: {response.data.get('detail')}")
elif response.status_code == 200:
    print(f"❌ SECURITY ISSUE! Private profile IS visible")
    print(f"  Returned data: {response.data}")
else:
    print(f"Unexpected status: {response.status_code}")

# STEP 3: Other user tries to search for ishan
print("\n" + "-" * 70)
print("STEP 3: Other user searches for ishan")
print("-" * 70)

request = factory.get(f'/api/users/search/?q={ishan.username}')
force_authenticate(request, user=other_user)
response = search_users(request)

print(f"Request: GET /api/users/search/?q={ishan.username}")
print(f"Response Status: {response.status_code}")
print(f"Results found: {len(response.data.get('results', []))}")

found_ishan = False
for user in response.data.get('results', []):
    if user['username'] == ishan.username:
        found_ishan = True
        print(f"❌ SECURITY ISSUE! Ishan found in search despite private profile")
        break

if not found_ishan:
    print(f"✓ CORRECT! Ishan NOT in search results (privacy filter working)")

# STEP 4: They become friends - now ishan should be visible
print("\n" + "-" * 70)
print(f"STEP 4: {ishan.username} and {other_user.username} become friends")
print("-" * 70)

FriendRequest.objects.create(
    from_user=other_user,
    to_user=ishan,
    status='accepted'
)
print("✓ Friend request created and accepted")

# STEP 5: Try again - should now be visible
print("\n" + "-" * 70)
print("STEP 5: After becoming friends, try viewing again")
print("-" * 70)

request = factory.get(f'/api/users/user-profile/{ishan.id}/')
force_authenticate(request, user=other_user)
response = get_user_profile(request, ishan.id)

print(f"Response Status: {response.status_code}")
if response.status_code == 200:
    print(f"✓ NOW VISIBLE as friends!")
    print(f"  Travel style: {response.data.get('travel_style')}")
    print(f"  Pace: {response.data.get('pace')}")
    print(f"  Accommodation: {response.data.get('accomodation_preference')}")
else:
    print(f"❌ UNEXPECTED: Should be visible to friends but got {response.status_code}")

# STEP 6: Search again - should now appear
print("\n" + "-" * 70)
print("STEP 6: Search again as friend")
print("-" * 70)

request = factory.get(f'/api/users/search/?q={ishan.username}')
force_authenticate(request, user=other_user)
response = search_users(request)

found_ishan = False
for user in response.data.get('results', []):
    if user['username'] == ishan.username:
        found_ishan = True
        break

if found_ishan:
    print(f"✓ Ishan NOW appears in search (friend can see)")
else:
    print(f"❌ Ishan should appear for friends but doesn't")

print("\n" + "=" * 70)
print("SCENARIO TEST COMPLETE")
print("=" * 70)

# Reset
ishan_profile.public_profile = True
ishan_profile.save()
