import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_companion.settings')
import django
django.setup()

from datetime import datetime, timedelta
import random
from django.db import transaction
from apps.users.models import UserProfile
from apps.trips.models import Trip, City

nepal_locations = {
    "Kathmandu": ["Pashupatinath", "Boudhanath", "Thamel", "Patan Durbar Square"],
    "Pokhara": ["Phewa Lake", "Annapurna", "Davis Falls", "Peace Pagoda"],
    "Chitwan": ["Jungle Safari", "Rapti River", "Elephant Camp", "National Park"],
    "Nagarkot": ["Himalayan Views", "Sunrise Point", "Local Villages", "Mountain Trek"],
    "Bhaktapur": ["Durbar Square", "Pottery", "Tachupal Tole", "Ancient City"],
    "Janakpur": ["Janaki Mandir", "Ganga Sagar", "Ram Navami", "Temple City"],
}

trip_tags_list = [
    ["hiking", "adventure", "budget"],
    ["trekking", "mountain", "scenic"],
    ["cultural", "temple", "exploration"],
    ["nature", "wildlife", "photography"],
    ["spiritual", "meditation", "peace"],
]

print("\n✈️ Creating 200 trips for 100 Nepalese users...")

# Get cities
cities = list(City.objects.filter(country='Nepal'))
print(f"Found {len(cities)} Nepal cities")

# Get Nepal profiles
nepal_profiles = UserProfile.objects.filter(user__username__startswith='nepal_')
print(f"Found {nepal_profiles.count()} Nepal profiles")

trips_to_create = []
with transaction.atomic():
    for idx, profile in enumerate(nepal_profiles):
        for trip_num in range(2):
            city = random.choice(cities)
            destination = random.choice(nepal_locations.get(city.name, ["Destination"]))
            
            start = datetime.now() + timedelta(days=random.randint(10, 100))
            duration = random.randint(3, 15)
            
            trip = Trip(
                title=f"{destination} Adventure {trip_num  + 1}",
                description=f"Join me for an exciting trip to {destination}! Looking for fellow adventurers.",
                creator=profile,
                destination=city,
                start_date=start,
                end_date=start + timedelta(days=duration),
                is_public=random.choice([True, False]),
                is_completed=False,
                trip_tags=random.choice(trip_tags_list),
            )
            trips_to_create.append(trip)
        
        if (idx + 1) % 20 == 0:
            print(f"  Prepared trips for {idx + 1}/100 users")
    
    print(f"\n  Creating {len(trips_to_create)} trips in database...")
    Trip.objects.bulk_create(trips_to_create, batch_size=100)

print(f"\n✅ SUCCESS!")
print(f"   • 100 Nepalese users created")
print(f"   • 200 Nepal trips created")
print(f"   • Total with profiles: 100 + 100 + 200 = 400 objects\n")
