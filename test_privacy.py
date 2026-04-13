#!/usr/bin/env python
"""Test privacy settings enforcement"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_companion.settings')
django.setup()

from django.contrib.auth.models import User
from django.db.models import Q
from apps.users.models import UserProfile, FriendRequest
from rest_framework.test import APIRequestFactory, force_authenticate
from apps.users.views_api import get_user_profile

print("=" * 60)
print("PRIVACY ENFORCEMENT TEST")
print("=" * 60)

# Get or create test users
users = list(User.objects.all()[:3])
if len(users) < 2:
    print("✗ Need at least 2 users in database. Found:", len(users))
    exit(1)

user1 = users[0]  # Someone trying to view a profile
user2 = users[1]  # The profile owner
user3 = users[2] if len(users) > 2 else None  # Optional third user

print(f"\nTest Setup:")
print(f"  User 1 (viewer): {user1.username}")
print(f"  User 2 (profile owner): {user2.username}")
if user3:
    print(f"  User 3 (for friendship test): {user3.username}")

# Ensure both have profiles
profile2 = user2.userprofile
profile1 = user1.userprofile

factory = APIRequestFactory()

# TEST 1: Public profile - visible to everyone
print("\n" + "-" * 60)
print("TEST 1: PUBLIC PROFILE")
print("-" * 60)

profile2.public_profile = True
profile2.save()
print(f"Set {user2.username}'s profile to PUBLIC")

request = factory.get(f'/users/user-profile/{user2.id}/')
force_authenticate(request, user=user1)
response = get_user_profile(request, user2.id)

print(f"Status Code: {response.status_code}")
if response.status_code == 200:
    print(f"✓ PUBLIC profile IS visible to non-friends (status 200)")
    print(f"  Data returned: username={response.data.get('username')}, bio={response.data.get('bio')}")
else:
    print(f"✗ FAILED - Expected 200, got {response.status_code}")

# TEST 2: Private profile - NOT visible to non-friends
print("\n" + "-" * 60)
print("TEST 2: PRIVATE PROFILE (non-friend)")
print("-" * 60)

profile2.public_profile = False
profile2.save()
print(f"Set {user2.username}'s profile to PRIVATE")

# No friendship between user1 and user2
FriendRequest.objects.filter(
    Q(from_user=user1, to_user=user2) | Q(from_user=user2, to_user=user1)
).delete()

request = factory.get(f'/users/user-profile/{user2.id}/')
force_authenticate(request, user=user1)
response = get_user_profile(request, user2.id)

print(f"Status Code: {response.status_code}")
if response.status_code == 403:
    print(f"✓ PRIVATE profile BLOCKED for non-friends (status 403)")
    print(f"  Message: {response.data.get('detail')}")
else:
    print(f"✗ FAILED - Expected 403, got {response.status_code}")
    print(f"  Data: {response.data}")

# TEST 3: Private profile - visible to friends
print("\n" + "-" * 60)
print("TEST 3: PRIVATE PROFILE (friend)")
print("-" * 60)

# Create accepted friend request
if user3:
    user3_profile = user3.userprofile
    # Make user1 and user2 friends
    FriendRequest.objects.filter(
        Q(from_user=user1, to_user=user2) | Q(from_user=user2, to_user=user1)
    ).delete()
    
    FriendRequest.objects.create(
        from_user=user1,
        to_user=user2,
        status='accepted'
    )
    print(f"Created ACCEPTED friend request: {user1.username} ↔ {user2.username}")
    
    request = factory.get(f'/users/user-profile/{user2.id}/')
    force_authenticate(request, user=user1)
    response = get_user_profile(request, user2.id)
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print(f"✓ PRIVATE profile VISIBLE to friends (status 200)")
        print(f"  Data returned: username={response.data.get('username')}, bio={response.data.get('bio')}")
    else:
        print(f"✗ FAILED - Expected 200, got {response.status_code}")

# TEST 4: Profile owner can always see their own profile
print("\n" + "-" * 60)
print("TEST 4: PRIVATE PROFILE (owner viewing own)")
print("-" * 60)

profile2.public_profile = False
profile2.save()
print(f"{user2.username}'s profile is PRIVATE")

request = factory.get(f'/users/user-profile/{user2.id}/')
force_authenticate(request, user=user2)  # Same user viewing own profile
response = get_user_profile(request, user2.id)

print(f"Status Code: {response.status_code}")
if response.status_code == 200:
    print(f"✓ Users CAN ALWAYS view their OWN profile (status 200)")
    print(f"  Data returned: username={response.data.get('username')}, bio={response.data.get('bio')}")
else:
    print(f"✗ FAILED - Expected 200, got {response.status_code}")

print("\n" + "=" * 60)
print("ALL PRIVACY ENFORCEMENT TESTS COMPLETED!")
print("=" * 60)

# Reset to public for normal use
profile2.public_profile = True
profile2.save()
