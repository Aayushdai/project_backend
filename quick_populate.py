import os
import django
from datetime import datetime, timedelta
import random

# Disable email sending
os.environ['EMAIL_BACKEND'] = 'django.core.mail.backends.dummy.EmailBackend'

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_companion.settings')
django.setup()

from django.db.models.signals import post_save
from django.contrib.auth.models import User as DjangoUser
from django.db import transaction

from apps.users.models import Interest, ConstraintTag, UserProfile
from apps.trips.models import Trip, City, TripExpenseBudget
from django.contrib.auth.models import User

print("=" * 60)
print("Creating 100 Nepalese Users - FAST VERSION")
print("=" * 60)

nepal_locations = {
    "Kathmandu": {"destinations": ["Pashupatinath", "Boudhanath", "Thamel"], "budget_range": (1000, 3000)},
    "Pokhara": {"destinations": ["Phewa Lake", "Annapurna View", "Davis Falls"], "budget_range": (800, 2500)},
    "Chitwan": {"destinations": ["Jungle Safari", "Rapti River"], "budget_range": (1200, 3500)},
}

names = ["Aditya", "Amit", "Anuj", "Arjun", "Ashok", "Abhishek", "Arun", "Aman", "Bikram", "Bhoj", "Chetan", "Chirag", "Darshan", "Deepak"]

# Get or create cities
cities = {}
for city_name in nepal_locations.keys():
    city, created = City.objects.get_or_create(name=city_name, defaults={"country": "Nepal"})
    cities[city_name] = city

print(f"✓ Cities: {len(cities)}")

interests = list(Interest.objects.all()[:5])
constraint_tags = list(ConstraintTag.objects.all()[:3])

# Disconnect signal
from apps.users.signals import create_user_profile
post_save.disconnect(create_user_profile, sender=DjangoUser)

users_created = 0

with transaction.atomic():
    for i in range(100):
        username = f"nepal_user_{i}"
        email = f"nepal_user_{i}@test.com"
        first = random.choice(names)
        last = random.choice(names)
        
        # Create user
        user, created = User.objects.get_or_create(
            username=username,
            defaults={'email': email, 'first_name': first, 'last_name': last}
        )
        
        if created:
            user.set_password('pass')
            user.save()
            users_created += 1
        
        # Create profile
        profile, _ = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'location': random.choice(list(nepal_locations.keys())),
                'citizenship': 'Nepal',
                'country': 'Nepal',
                'travel_style': 'budget',
                'pace': 'moderate',
            }
        )
        
        # Add interests/tags if any
        if interests:
            profile.interests.set(interests[:2])
        if constraint_tags:
            profile.constraint_tags.set(constraint_tags[:1])
        
        if (i + 1) % 20 == 0:
            print(f"✓ {i + 1} users created")

# Reconnect signal
post_save.connect(create_user_profile, sender=DjangoUser)

print(f"\n✓ Total users: {users_created}")

# Create trips
print("\nCreating trips...")
all_users = UserProfile.objects.filter(user__username__startswith='nepal_user_')
trip_count = 0

with transaction.atomic():
    for user_profile in all_users:
        for j in range(2):
            city = random.choice(list(cities.values()))
            start = datetime.now() + timedelta(days=random.randint(10, 60))
            end = start + timedelta(days=random.randint(3, 15))
            
            trip = Trip.objects.create(
                title=f"Trip {j+1}",
                description="Amazing trip",
                creator=user_profile,
                destination=city,
                start_date=start,
                end_date=end,
                is_public=True,
            )
            
            TripExpenseBudget.objects.create(trip=trip, category="Food", amount=500)
            trip_count += 1

print(f"✓ Trips created: {trip_count}")
print("\n✅ Done!\n")
