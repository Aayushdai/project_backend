import os
import django
from datetime import datetime, timedelta
import random

# Disable email sending during population
os.environ['EMAIL_BACKEND'] = 'django.core.mail.backends.dummy.EmailBackend'
os.environ['CELERY_TASK_ALWAYS_EAGER'] = 'true'

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_companion.settings')
django.setup()

from django.db import transaction
from django.contrib.auth.models import User as DjangoUser
from apps.users.models import UserProfile, ConstraintTag
from apps.trips.models import Trip, City

print("=" * 70)
print("Creating 20 Chitwan Trips with 10 Person Groups (Diverse Tags)")
print("=" * 70)

# Nepali names
nepali_first_names = [
    "Aditya", "Amit", "Anuj", "Arjun", "Ashok", "Abhishek", "Arun", "Aman",
    "Priya", "Pooja", "Pratima", "Parita", "Prama", "Prisha",
    "Bikram", "Bhoj", "Bhuwan", "Bhaskar", "Bimal", "Binod",
    "Chetan", "Chirag", "Chhabi", "Chandra", "Champa",
    "Deepak", "Devendra", "Dawa", "Dipak", "Devi",
]

nepali_last_names = [
    "Acharya", "Adhikari", "Agrawal", "Aryal",
    "Bajaj", "Bhat", "Bhattacharya",
    "Chhetri", "Chopra", "Choudhary",
    "Dhakal", "Dhawan",
    "Giri", "Goel", "Gowda", "Gupta",
    "Iyer", "Jain", "Joshi",
]

# Get or create Chitwan city
chitwan_city, _ = City.objects.get_or_create(
    name="Chitwan",
    defaults={
        "country": "Nepal",
        "latitude": 27.5922,
        "longitude": 84.5094,
    }
)

print(f"\n✓ Using city: {chitwan_city.name}, {chitwan_city.country}")

# ============================================================
# CREATE USERS WITH DIVERSE TAGS
# ============================================================
print("\n👥 Creating 200 users with diverse personality tags...")

users_created = 0
user_profiles = []
django_users_to_create = []

with transaction.atomic():
    # Prepare all users first
    for idx in range(200):
        first_name = random.choice(nepali_first_names)
        last_name = random.choice(nepali_last_names)
        username = f"chitwan_user_{idx + 1:03d}"
        email = f"chitwan_user_{idx + 1:03d}@travelcompanion.test"
        
        # Check if user already exists
        if not DjangoUser.objects.filter(username=username).exists():
            django_user = DjangoUser(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
            )
            django_users_to_create.append(django_user)
    
    # Bulk create Django users
    if django_users_to_create:
        print(f"  ✓ Creating {len(django_users_to_create)} Django users in bulk...")
        created_users = DjangoUser.objects.bulk_create(django_users_to_create, batch_size=50)
        print(f"  ✓ Created {len(created_users)} Django users")
    
    # Now get all users and create profiles with tags
    all_django_users = DjangoUser.objects.filter(username__startswith='chitwan_user_')
    print(f"  ✓ Found {all_django_users.count()} total Django users")
    
    for idx, django_user in enumerate(all_django_users):
        # Create profile if it doesn't exist
        user_profile, created = UserProfile.objects.get_or_create(
            user=django_user,
            defaults={
                'bio': f"Love Chitwan adventures!",
                'phone': f"+977 98{random.randint(10000000, 99999999)}",
            }
        )
        
        if created:
            # Assign diverse personality tags (3-5 tags per person)
            num_tags = random.randint(3, 5)
            all_tags = list(ConstraintTag.objects.all())
            selected_tags = random.sample(all_tags, min(num_tags, len(all_tags)))
            user_profile.constraint_tags.set(selected_tags)
            users_created += 1
        
        user_profiles.append(user_profile)
        
        if (idx + 1) % 50 == 0:
            print(f"  ✓ Processed {idx + 1} users with personality tags")

print(f"✓ Successfully prepared {users_created} users with diverse tags")

# ============================================================
# CREATE 20 CHITWAN TRIPS WITH "CHITWAN" IN THE NAME
# ============================================================
print(f"\n✈️  Creating 20 Chitwan trips with 10 person groups...")

trips_created = 0
base_date = datetime.now() + timedelta(days=10)

# All trip names with "Chitwan" 
CHITWAN_TRIP_NAMES = [
    "Chitwan Jungle Safari",
    "Chitwan Wildlife Adventure",
    "Chitwan Elephant Camp",
    "Chitwan National Park Explorer",
    "Chitwan River Rafting",
    "Chitwan Adventure Group",
    "Chitwan Nature Trek",
    "Chitwan Budget Tour",
    "Chitwan Luxury Experience",
    "Chitwan Eco Tour",
    "Chitwan Backpacker Trail",
    "Chitwan Weekend Escape",
    "Chitwan Jungle Explorers",
    "Chitwan Wildlife Photography",
    "Chitwan Adventure Squad",
    "Chitwan Nature Lovers",
    "Chitwan Thrill Seekers",
    "Chitwan Group Trip",
    "Chitwan Family Adventure",
    "Chitwan Friends Getaway",
]

with transaction.atomic():
    for trip_idx in range(20):
        # Select a creator from our users
        creator = random.choice(user_profiles)
        
        # Create trip
        trip = Trip.objects.create(
            title=CHITWAN_TRIP_NAMES[trip_idx],
            description=f"Join us for an amazing {CHITWAN_TRIP_NAMES[trip_idx]} experience! "
                       f"Perfect for 10 travelers looking to explore Chitwan together. "
                       f"Let's make unforgettable memories!",
            creator=creator,
            destination=chitwan_city,
            start_date=base_date + timedelta(days=random.randint(0, 60)),
            end_date=base_date + timedelta(days=random.randint(3, 15)),
            is_public=True,
            is_completed=False,
            trip_tags=random.choice([
                ["adventure", "wildlife", "safari"],
                ["nature", "hiking", "exploration"],
                ["jungle", "camping", "wildlife"],
                ["budget", "backpacking", "adventure"],
                ["luxury", "nature", "experience"],
            ]),
        )
        
        # Add exactly 10 participants to this trip
        num_participants = 10
        
        # Get available users (exclude creator)
        available_users = [u for u in user_profiles if u != creator]
        selected_participants = random.sample(available_users, min(num_participants, len(available_users)))
        
        # Add them to the trip
        trip.participants.set(selected_participants)
        
        trips_created += 1
        
        print(f"  ✓ Trip {trip_idx + 1}/20: '{trip.title}' ({len(selected_participants)} participants)")

print(f"\n✓ Successfully created {trips_created} Chitwan trips")

# ============================================================
# VERIFICATION & SUMMARY
# ============================================================
print("\n" + "=" * 70)
print("📊 VERIFICATION & SUMMARY")
print("=" * 70)

total_users = UserProfile.objects.filter(user__username__startswith='chitwan_user_').count()
total_trips = Trip.objects.filter(destination=chitwan_city, creator__user__username__startswith='chitwan_user_').count()

print(f"\n✓ Total users created: {total_users}")
print(f"✓ Total Chitwan trips created: {total_trips}")

# Show sample of users with their tags
print(f"\n📋 Sample Users with Personality Tags:")
sample_users = random.sample(user_profiles, min(5, len(user_profiles)))
for idx, user in enumerate(sample_users, 1):
    tags = [tag.name for tag in user.constraint_tags.all()]
    print(f"  {idx}. {user.user.first_name} {user.user.last_name}")
    print(f"     Tags: {', '.join(tags[:4])}")

# Show sample trips with participants
print(f"\n✈️  Sample Trips with Group Sizes:")
sample_trips = Trip.objects.filter(destination=chitwan_city).order_by('-created_at')[:5]
for idx, trip in enumerate(sample_trips, 1):
    participant_count = trip.participants.count()
    print(f"  {idx}. {trip.title}")
    print(f"     Group Size: {participant_count} participants")

print("\n" + "=" * 70)
print("✅ TASK COMPLETED!")
print("=" * 70)
print(f"\n📍 Chitwan test data ready!")
print(f"   • 200 users with diverse personality tags")
print(f"   • 20 Chitwan trips with exactly 10 people each")
print(f"   • All trip names have 'Chitwan' in them")
print(f"   • Tags cover: diet, lifestyle, values, age, gender, status")
