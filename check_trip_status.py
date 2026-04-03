#!/usr/bin/env python
"""Test joining an un-joined trip"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_companion.settings')
django.setup()

from django.contrib.auth.models import User
from apps.trips.models import Trip
from datetime import date

user = User.objects.get(username='aayush')
user_profile = user.userprofile

print("=" * 70)
print("CHECKING TRIP PARTICIPATION STATUS")
print("=" * 70)

# Check both future trips
future_trips = Trip.objects.filter(end_date__gte=date.today(), is_public=True)

for trip in future_trips:
    is_participant = trip.participants.filter(id=user_profile.id).exists()
    status_symbol = "✓ JOINED" if is_participant else "○ NOT JOINED"
    participants = list(trip.participants.values_list('user__username', flat=True))
    
    print(f"\n{status_symbol} | Trip ID {trip.id}: {trip.title}")
    print(f"       Creator: {trip.creator.user.username}")
    print(f"       Participants ({trip.participants.count()}): {', '.join(participants)}")
    print(f"       Dates: {trip.start_date} to {trip.end_date}")
    
    if is_participant:
        # Check if they can leave
        other_participants = trip.participants.exclude(id=user_profile.id).count()
        can_leave = trip.creator != user_profile
        print(f"       Can leave: {can_leave}")
    else:
        # Check if they can join
        is_ended = trip.end_date < date.today()
        can_join = not is_ended
        print(f"       Can join: {can_join}")

print("\n" + "=" * 70)
print("\nSUMMARY:")
print("If patan (ID 9) shows 'NOT JOINED', you should be able to join it.")
print("If 'Test Trip' (ID 1) shows 'JOINED', you're already in it.")
