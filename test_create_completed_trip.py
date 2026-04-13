#!/usr/bin/env python
import os
import django
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_companion.settings')
django.setup()

from apps.trips.models import Trip
from apps.users.models import UserProfile
from apps.core.models import City

# Get first user
user = UserProfile.objects.first()
print(f"👤 Testing with user: {user.user.username}")

# Get or create a city
city = City.objects.first()
if not city:
    print("❌ No cities found in database")
    exit()

# Create a test trip with past end date
past_date = date.today() - timedelta(days=5)
start_date = date.today() - timedelta(days=10)

test_trip = Trip.objects.create(
    title="Test Completed Trip ABC",
    city=city,
    start_date=start_date,
    end_date=past_date,
    creator=user,
    is_public=True,
    is_completed=False,  # Will be auto-marked by the logic
)

print(f"\n📌 Created test trip:")
print(f"   Title: {test_trip.title}")
print(f"   End date: {test_trip.end_date}")
print(f"   Is completed (before): {test_trip.is_completed}")

# Run auto-mark logic (simulates what happens when /api/trips/ is called)
updated = Trip.objects.filter(end_date__lt=date.today(), is_completed=False).update(is_completed=True)
print(f"\n🔄 Auto-mark logic ran: Updated {updated} trips")

# Refresh from DB
test_trip.refresh_from_db()
print(f"   Is completed (after): {test_trip.is_completed}")

# Count completed trips for user
user_trips = Trip.objects.filter(participants=user) | Trip.objects.filter(creator=user)
completed = user_trips.filter(is_completed=True).count()
print(f"\n✨ Completed trips for {user.user.username}: {completed}")
print(f"📱 Profile should display: {completed}")

# Cleanup
test_trip.delete()
print(f"\n🧹 Cleaned up test trip")
