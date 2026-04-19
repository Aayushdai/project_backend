"""
Compare trip_tags in database with TRIP_TAGS_CATEGORIES in frontend
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_companion.settings')
django.setup()

from apps.trips.models import Trip

# These should match the frontend TRIP_TAGS_CATEGORIES
FRONTEND_TAGS = {
    "Trip Type": ["Adventure", "Relaxation", "Cultural", "Nature", "Road Trip", "Backpacking", "Trekking / Hiking", "Camping", "City Tour", "Beach Trip", "Wildlife / Safari"],
    "Budget Level": ["Budget", "Mid-range", "Luxury"],
    "Activity Level": ["High Activity", "Moderate Activity", "Chill / Low Activity"],
    "Trip Style": ["Solo Friendly", "Group Trip", "Family Friendly", "Friends Trip", "Guided Tour", "DIY / Self-planned"],
    "Environment": ["Mountain", "Hills", "Forest", "Lake / Riverside", "Desert", "Urban", "Rural / Village"],
    "Duration": ["Weekend Trip", "Short Trip (2–3 days)", "Long Trip (4+ days)"],
    "Transport": ["Road Trip", "Flight Travel", "Mixed Transport"],
    "Purpose": ["Photography", "Food Exploration", "Sightseeing", "Spiritual / Religious", "Party / Nightlife", "Wellness / Retreat", "Festival Trip"],
    "Stay Type": ["Hotel Stay", "Homestay", "Camping Stay", "Resort Stay"]
}

# Flatten all frontend tags
all_frontend_tags = set()
for category, tags in FRONTEND_TAGS.items():
    all_frontend_tags.update(tags)

print("Frontend Tags (defined in code):")
print("=" * 80)
for tag in sorted(all_frontend_tags):
    print(f"  - {tag}")

print(f"\nTotal Frontend Tags: {len(all_frontend_tags)}")

# Check what's in database
print("\n\nTrips and their tags:")
print("=" * 80)
trips = Trip.objects.all().order_by('-id')[:5]
for trip in trips:
    trip_tags = trip.trip_tags or []
    print(f"\n📍 Trip: {trip.title}")
    print(f"   Tags: {trip_tags}")
    
    # Check which tags are NOT in frontend tags
    invalid_tags = set(trip_tags) - all_frontend_tags
    if invalid_tags:
        print(f"   ⚠️  INVALID tags (not in frontend): {invalid_tags}")
    else:
        print(f"   ✅ All tags valid!")

# Check for tags in database that aren't in frontend
print("\n\nAll unique tags in database (across all trips):")
print("=" * 80)
all_db_tags = set()
for trip in Trip.objects.all():
    trip_tags = trip.trip_tags or []
    all_db_tags.update(trip_tags)

print(f"Total unique tags in database: {len(all_db_tags)}")
for tag in sorted(all_db_tags):
    in_frontend = "✅" if tag in all_frontend_tags else "❌"
    print(f"  {in_frontend} {tag}")

# Find mismatch
invalid_db_tags = all_db_tags - all_frontend_tags
if invalid_db_tags:
    print(f"\n\n🚨 MISMATCH FOUND!")
    print(f"Tags in database but NOT in frontend filter:")
    for tag in sorted(invalid_db_tags):
        print(f"  - {tag}")
