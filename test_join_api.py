#!/usr/bin/env python
"""Test the join trip functionality end-to-end"""

import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_companion.settings')
django.setup()

from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from apps.trips.models import Trip
from django.test import Client
from datetime import date

# Get aayush user
user = User.objects.get(username='aayush')
user_profile = user.userprofile

print("=" * 60)
print("TESTING JOIN TRIP FUNCTIONALITY")
print("=" * 60)

# Generate JWT token for aayush
refresh = RefreshToken.for_user(user)
access_token = str(refresh.access_token)

print(f"\n✓ User: {user.username}")
print(f"✓ Access Token: {access_token[:50]}...")

# Get available trip
trip = Trip.objects.filter(end_date__gte=date.today(), is_public=True).first()

if not trip:
    print("❌ No future public trips available!")
else:
    print(f"✓ Trip: {trip.title} (ID: {trip.id})")
    print(f"  Participants before: {trip.participants.count()}")
    print(f"  Is already participant: {trip.participants.filter(id=user_profile.id).exists()}")
    
    # Simulate the API request
    client = Client()
    
    # Make PATCH request to join
    print(f"\n→ Making PATCH request to /api/trips/trips/{trip.id}/")
    print(f"  Headers: Authorization: Bearer {access_token[:30]}...")
    print(f"  Body: {{'action': 'join'}}")
    
    response = client.patch(
        f"/api/trips/trips/{trip.id}/",
        data=json.dumps({"action": "join"}),
        content_type="application/json",
        HTTP_AUTHORIZATION=f"Bearer {access_token}"
    )
    
    print(f"\n← Response Status: {response.status_code}")
    print(f"← Response Data: {response.json()}")
    
    # Check if join was successful
    trip.refresh_from_db()
    print(f"\n✓ Trip participants after: {trip.participants.count()}")
    print(f"✓ Is now participant: {trip.participants.filter(id=user_profile.id).exists()}")
    
    if response.status_code == 200:
        print("\n✅ JOIN SUCCESSFUL!")
    else:
        print(f"\n❌ JOIN FAILED - Status {response.status_code}")
        if "message" in response.json():
            print(f"   Error: {response.json()['message']}")

print("\n" + "=" * 60)
