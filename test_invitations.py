#!/usr/bin/env python
"""
Test Trip Invitation Endpoints
Run this from Travel_Companion_Backend directory:
  python test_invitations.py
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_companion.settings')
django.setup()

from django.contrib.auth.models import User
from apps.users.models import UserProfile
from apps.trips.models import Trip
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
import json

def test_invitations():
    print("=" * 60)
    print("Testing Trip Invitation Endpoints")
    print("=" * 60)
    
    client = APIClient()
    
    # Create test users
    print("\n1️⃣ Creating test users...")
    try:
        creator_user = User.objects.create_user(
            username='trip_creator',
            email='creator@test.com',
            first_name='Trip',
            last_name='Creator',
            password='testpass123'
        )
        creator_profile = UserProfile.objects.create(user=creator_user)
        print(f"   ✓ Creator: {creator_user.username} (ID: {creator_profile.id})")
    except:
        creator_user = User.objects.get(username='trip_creator')
        creator_profile = creator_user.userprofile
        print(f"   ✓ Creator exists: {creator_user.username} (ID: {creator_profile.id})")
    
    try:
        invitee_user = User.objects.create_user(
            username='trip_invitee',
            email='invitee@test.com',
            first_name='Trip',
            last_name='Invitee',
            password='testpass123'
        )
        invitee_profile = UserProfile.objects.create(user=invitee_user)
        print(f"   ✓ Invitee: {invitee_user.username} (ID: {invitee_profile.id})")
    except:
        invitee_user = User.objects.get(username='trip_invitee')
        invitee_profile = invitee_user.userprofile
        print(f"   ✓ Invitee exists: {invitee_user.username} (ID: {invitee_profile.id})")
    
    # Get or create token for creator
    print("\n2️⃣ Getting authentication token...")
    token, _ = Token.objects.get_or_create(user=creator_user)
    client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
    print(f"   ✓ Token: {token.key[:20]}...")
    
    # Get test trip
    print("\n3️⃣ Getting test trip...")
    try:
        trip = Trip.objects.first()
        if not trip:
            print("   ❌ No trips found in database!")
            return
        print(f"   ✓ Trip: {trip.title} (ID: {trip.id})")
    except Exception as e:
        print(f"   ❌ Error getting trip: {e}")
        return
    
    # Test: Send invitation
    print("\n4️⃣ Testing POST /api/trips/{trip_id}/invitations/...")
    try:
        response = client.post(
            f'/api/trips/{trip.id}/invitations/',
            {
                'invited_user': invitee_profile.id,
                'role': 'member'
            },
            format='json'
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 201:
            print("   ✓ Invitation created successfully!")
        else:
            print(f"   ❌ Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test: List invitations
    print("\n5️⃣ Testing GET /api/trips/{trip_id}/invitations/...")
    try:
        response = client.get(f'/api/trips/{trip.id}/invitations/')
        print(f"   Status: {response.status_code}")
        invitations = response.json()
        print(f"   Found {len(invitations)} invitation(s)")
        for inv in invitations:
            print(f"      - {inv.get('invited_user_name')} ({inv.get('status')})")
        print("   ✓ Listing successful!")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test: Generate invite link
    print("\n6️⃣ Testing POST /api/trips/{trip_id}/generate-invite-link/...")
    try:
        response = client.post(f'/api/trips/{trip.id}/generate-invite-link/')
        print(f"   Status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
        print("   ✓ Link generated successfully!")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test: Get user suggestions
    print("\n7️⃣ Testing GET /api/users/suggestions/?trip_id={trip_id}...")
    try:
        response = client.get(f'/api/users/suggestions/?trip_id={trip.id}')
        print(f"   Status: {response.status_code}")
        suggestions = response.json()
        print(f"   Found {len(suggestions)} suggestion(s)")
        for user in suggestions[:3]:
            print(f"      - {user.get('name')} ({user.get('similarity')}% match)")
        print("   ✓ Suggestions retrieved!")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Test Complete!")
    print("=" * 60)

if __name__ == '__main__':
    test_invitations()
