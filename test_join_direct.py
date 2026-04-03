#!/usr/bin/env python
"""Test the actual join API call"""

import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_companion.settings')
django.setup()

from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from apps.trips.models import Trip
from datetime import date
from django.test import RequestFactory
from apps.trips.views import TripDetailAPIView

# Get user and token
user = User.objects.get(username='aayush')
trip = Trip.objects.get(id=9)  # patan trip

print("=" * 70)
print("TESTING JOIN ENDPOINT DIRECTLY")
print("=" * 70)

print(f"\nUser: {user.username}")
print(f"Trip: {trip.title} (ID: {trip.id})")
print(f"Current Participants: {trip.participants.count()}")

# Create a PATCH request using RequestFactory
factory = RequestFactory()
refresh = RefreshToken.for_user(user)
access_token = str(refresh.access_token)

# Simulate the PATCH request
request = factory.patch(
    f'/api/trips/trips/{trip.id}/',
    data=json.dumps({"action": "join"}),
    content_type='application/json',
    HTTP_AUTHORIZATION=f'Bearer {access_token}'
)

# Manually set user on request
from rest_framework.request import Request as DRFRequest
request = DRFRequest(request)
request.user = user

print(f"\n→ Calling TripDetailAPIView.patch() with action='join'")

# Call the view
view = TripDetailAPIView()
try:
    response = view.patch(request, pk=trip.id)
    
    print(f"\n← Response Status: {response.status_code}")
    print(f"← Response Data:")
    
    if hasattr(response, 'data'):
        import json
        print(json.dumps(response.data, indent=2, default=str))
    
    # Refresh and check
    trip.refresh_from_db()
    is_now_participant = trip.participants.filter(id=user.userprofile.id).exists()
    
    print(f"\n✓ Participants after join: {trip.participants.count()}")
    print(f"✓ User is now participant: {is_now_participant}")
    
    if response.status_code == 200 and is_now_participant:
        print("\n✅ JOIN SUCCESSFUL!")
    else:
        print(f"\n❌ JOIN FAILED")
        
except Exception as e:
    print(f"\n❌ ERROR: {type(e).__name__}")
    print(f"   {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
