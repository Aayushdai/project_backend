#!/usr/bin/env python
import os
import django
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_companion.settings')
django.setup()

from apps.trips.models import Trip
from apps.users.models import UserProfile

# Get first user
user = UserProfile.objects.first()
if not user:
    print("❌ No users found in database")
    exit()

print(f"👤 User: {user.user.username}")
print(f"🏠 Profile ID: {user.id}")

# Get all their trips (as participant or creator)
user_trips = Trip.objects.filter(participants=user) | Trip.objects.filter(creator=user)
print(f"\n📊 Total trips: {user_trips.count()}")

# Show trip details
print("\n🔍 Trip Details:")
for i, trip in enumerate(user_trips[:5], 1):
    days_passed = (date.today() - trip.end_date).days
    status = "✅ COMPLETED" if trip.is_completed else "❌ NOT COMPLETED"
    print(f"\n  [{i}] {trip.title}")
    print(f"      End date: {trip.end_date}")
    print(f"      Status: {status}")
    print(f"      Days passed: {days_passed}")
    print(f"      Should be completed: {days_passed > 0}")

# Manually trigger the auto-mark logic
print("\n🔄 Running auto-mark logic...")
updated = Trip.objects.filter(end_date__lt=date.today(), is_completed=False).update(is_completed=True)
print(f"   Updated {updated} trips to completed")

# Count completed trips
completed_trips = user_trips.filter(is_completed=True).count()
print(f"\n✨ Completed trips after auto-mark: {completed_trips}")

# Show the fixed count
print(f"\n📱 Profile should show: {completed_trips} completed trips")
