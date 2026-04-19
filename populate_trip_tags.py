"""
Script to populate trip_tags for existing trips that don't have tags
"""
import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_companion.settings')
django.setup()

from apps.trips.models import Trip

TRIP_TAGS_CATEGORIES = {
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

# Flatten all tags
ALL_TAGS = []
for category, tags in TRIP_TAGS_CATEGORIES.items():
    ALL_TAGS.extend(tags)

print(f"Found {len(ALL_TAGS)} unique tags")

# Get trips without tags
trips_without_tags = Trip.objects.filter(trip_tags=[])
print(f"\nFound {trips_without_tags.count()} trips without tags")

# Populate tags
updated_count = 0
for trip in trips_without_tags:
    # Assign 3-5 random tags to each trip
    num_tags = random.randint(3, 5)
    trip.trip_tags = random.sample(ALL_TAGS, min(num_tags, len(ALL_TAGS)))
    trip.save()
    updated_count += 1
    print(f"✅ Updated {trip.title}: {trip.trip_tags}")

print(f"\n✅ Successfully updated {updated_count} trips with tags")
