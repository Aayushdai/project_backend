#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_companion.settings')
django.setup()

from apps.users.models import UserProfile, Interest

# Check Nepal users
nepal_users = UserProfile.objects.filter(user__username__startswith='nepal_')
print(f"Nepal users found: {nepal_users.count()}")

if nepal_users.exists():
    for user in nepal_users[:3]:
        interests = user.interests.count()
        print(f"  {user.user.username}: {interests} interests")
else:
    print("⚠️  No nepal_ users found")

# Check all interests in the system
print(f"\nTotal interests in system: {Interest.objects.count()}")
print(f"Sample interests: {[i.name for i in Interest.objects.all()[:5]]}")

# Check if any user has interests
users_with_interests = UserProfile.objects.filter(interests__isnull=False).distinct().count()
print(f"\nUsers with interests: {users_with_interests}")

# Check trip participants
from apps.trips.models import Trip
trips = Trip.objects.filter(is_public=True)[:3]
print(f"\nTrip participant details:")
for trip in trips:
    print(f"  {trip.title}: {trip.participants.count()} participants")
    for p in trip.participants.all()[:2]:
        print(f"    - {p.user.username}: {p.interests.count()} interests")
