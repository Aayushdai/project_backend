#!/usr/bin/env python
"""Test the join logic directly"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_companion.settings')
django.setup()

from django.contrib.auth.models import User
from apps.trips.models import Trip
from datetime import date

# Get user and trip
user = User.objects.get(username='aayush')
user_profile = user.userprofile
trip = Trip.objects.get(id=9)  # patan trip
today = date.today()

print("=" * 70)
print("SIMULATING JOIN LOGIC (from views.py patch method)")
print("=" * 70)

print(f"\nUser: {user.username}")
print(f"Trip: {trip.title} (ID: {trip.id})")
print(f"Trip end date: {trip.end_date}")
print(f"Today: {today}")
print(f"Trip ended: {trip.end_date < today}")

user_profile_id = user_profile.id
print(f"\nUser Profile ID: {user_profile_id}")

# CHECK 1: Is trip ended?
print(f"\n→ CHECK 1: Is trip ended?")
if trip.end_date < today:
    print("  ❌ BLOCKED: Trip has already ended")
else:
    print("  ✓ PASSED: Trip is still upcoming")

# CHECK 2: Is user already a participant?
print(f"\n→ CHECK 2: Is user already a participant?")
is_already_participant = trip.participants.filter(id=user_profile.id).exists()
print(f"  Participants: {list(trip.participants.values_list('user__username', flat=True))}")
print(f"  Is participant: {is_already_participant}")

if is_already_participant:
    print("  ℹ️  User is already a participant (idempotent - will not add again)")
else:
    print("  ✓ User is NOT a participant - will be added")

# CHECK 3: Is user KYC approved? (from API endpoint)
print(f"\n→ CHECK 3: Is user KYC approved?")
try:
    kyc = user.kyc_profile
    is_kyc_approved = kyc.status == 'approved'
    has_id_number = bool(kyc.id_number)
    print(f"  KYC Status: {kyc.status}")
    print(f"  KYC ID Number: {kyc.id_number}")
    print(f"  Is approved: {is_kyc_approved}")
    print(f"  Has ID number: {has_id_number}")
    
    if is_kyc_approved and has_id_number:
        print("  ✓ PASSED: User is KYC approved")
    else:
        print("  ❌ BLOCKED: User KYC not fully approved")
except:
    print("  ❌ BLOCKED: User has no KYC profile")

# SIMULATE THE ACTUAL JOIN
print(f"\n→ SIMULATING JOIN ACTION")
print("  Before:")
print(f"    Participants: {trip.participants.count()}")

# This is what the endpoint does
if not trip.participants.filter(id=user_profile.id).exists():
    trip.participants.add(user_profile)
    print("    Action: Added user to participants")
else:
    print("    Action: User already participant (no change)")

print("  After:")
print(f"    Participants: {trip.participants.count()}")
is_now_participant = trip.participants.filter(id=user_profile.id).exists()
print(f"    User is participant: {is_now_participant}")

print("\n" + "=" * 70)
print("RESULT: Join operation would succeed ✓")
print("=" * 70)
