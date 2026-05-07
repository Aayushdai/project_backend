import os
import django
from datetime import datetime, timedelta
import random

# Disable email sending during population
os.environ['EMAIL_BACKEND'] = 'django.core.mail.backends.dummy.EmailBackend'
os.environ['CELERY_TASK_ALWAYS_EAGER'] = 'true'  # Disable async tasks

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_companion.settings')
django.setup()

# Disable signals to speed up creation
from django.db.models.signals import post_save, pre_save
from apps.users.models import UserProfile as UserProfileModel

# Disconnect signals
post_save.disconnect(dispatch_uid='all')

from django.db import transaction
from django.contrib.auth.models import User as DjangoUser
from apps.users.models import UserProfile, ConstraintTag, Interest
from apps.trips.models import Trip, City

print("=" * 70)
print("Creating 20 Kathmandu Trips with 10+ Person Groups (Diverse Tags)")
print("=" * 70)

# ============================================================
# PERSONALITY TAGS - DIVERSE COVERAGE
# ============================================================
DIVERSE_TAG_COMBINATIONS = [
    # Group 1: Adventure Seekers
    ["Adventure Seeker", "Fitness Focused", "Early Riser", "Non-smoker"],
    # Group 2: Luxury & Comfort
    ["Luxury Lover", "Party Person", "Drinks Alcohol", "Extrovert"],
    # Group 3: Budget Conscious Backpackers
    ["Budget Conscious", "Quiet Traveler", "Vegetarian", "Eco-conscious"],
    # Group 4: Spiritual & Cultural
    ["Religious/Spiritual", "Quiet & Homebody", "Non-drinker", "Introvert"],
    # Group 5: Night Life Lovers
    ["Party Person", "Night Owl", "Smoker", "Extrovert"],
    # Group 6: Nature & Peace Seekers
    ["Eco-conscious", "Minimalist", "Early Riser", "Quiet Traveler"],
    # Group 7: Fitness & Wellness
    ["Fitness Focused", "Non-smoker", "Non-drinker", "Eco-conscious"],
    # Group 8: Social & Active
    ["Social Butterfly", "Adventure Seeker", "Extrovert", "Party Person"],
    # Group 9: Cultural Explorers
    ["Religious/Spiritual", "Eco-conscious", "Quiet Traveler", "Introvert"],
    # Group 10: Luxury Health Conscious
    ["Luxury Lover", "Fitness Focused", "Non-smoker", "Vegetarian"],
]

# Extended personality traits for 10+ people per trip
PERSONALITY_TRAITS = {
    "diet": ["Vegetarian", "Non-vegetarian", "Vegan", "Pescatarian", "Halal"],
    "lifestyle": ["Non-smoker", "Smoker", "Early Riser", "Night Owl", "Fitness Focused", "Party Person", "Quiet & Homebody"],
    "values": ["Adventure Seeker", "Budget Conscious", "Luxury Lover", "Eco-conscious", "Quiet Traveler", "Social Butterfly", "Religious/Spiritual", "Introvert", "Extrovert"],
    "age_range": ["18-25", "25-35", "35-50"],
    "gender": ["Men Only", "Women Only", "Mixed Group"],
    "status": ["Single", "Solo Traveler"],
}

# Trip themes for Kathmandu
TRIP_THEMES = [
    "Kathmandu Heritage Explorer",
    "Temple & Spiritual Journey",
    "Urban Adventure in Kathmandu",
    "Kathmandu Food & Culture",
    "Thamel District Adventure",
    "Durbar Square Discovery",
    "Kathmandu Valley Trek",
    "Buddhist Pilgrimage Route",
    "Modern Kathmandu Experience",
    "Kathmandu Night Life",
    "Local Life in Kathmandu",
    "Kathmandu Art & History",
    "Sacred Sites Tour",
    "Kathmandu Weekend Getaway",
    "Mountain View from Kathmandu",
    "Kathmandu Party Circuit",
    "Budget Backpacker Route",
    "Luxury Kathmandu Experience",
    "Kathmandu Photography Tour",
    "Student Travel in Kathmandu",
]

# Get or create Kathmandu city
kathmandu_city, _ = City.objects.get_or_create(
    name="Kathmandu",
    defaults={
        "country": "Nepal",
        "latitude": 27.7172,
        "longitude": 85.3240,
    }
)

print(f"\n✓ Using city: {kathmandu_city.name}, {kathmandu_city.country}")

# Get or create constraint tags
print("\n📝 Ensuring all personality tags exist...")
created_tags = []
for category, tags in PERSONALITY_TRAITS.items():
    for tag_name in tags:
        tag, created = ConstraintTag.objects.get_or_create(
            name=tag_name,
            category=category,
            defaults={'description': f'{tag_name} - personality trait'}
        )
        if created:
            created_tags.append(tag_name)

if created_tags:
    print(f"  ✓ Created {len(created_tags)} new tags: {', '.join(created_tags[:5])}...")

# ============================================================
# CREATE USERS WITH DIVERSE TAGS
# ============================================================
print("\n👥 Creating 200 users with diverse personality tags...")

nepali_first_names = [
    "Aditya", "Amit", "Anuj", "Arjun", "Ashok", "Abhishek", "Arun", "Aman",
    "Priya", "Pooja", "Pratima", "Parita", "Prama", "Prisha",
    "Bikram", "Bhoj", "Bhuwan", "Bhaskar", "Bimal", "Binod",
    "Chetan", "Chirag", "Chhabi", "Chandra", "Champa",
    "Deepak", "Devendra", "Dawa", "Dipak", "Devi",
    "Gagan", "Ganesh", "Gendra", "Girish", "Gaurav",
    "Hari", "Harendra", "Himal", "Hemanta",
    "Jaya", "Jatan", "Jayendra", "Jeevan",
    "Kalyan", "Kamal", "Kapil", "Karun",
    "Lal", "Lama", "Lokendra",
    "Madan", "Mahendra", "Mangal", "Manish", "Manoj", "Mohan",
    "Nabin", "Naresh", "Narendra", "Nayan", "Nikhil",
    "Prabhat", "Prabhakar", "Pradeep", "Pranav", "Prasad",
    "Raj", "Rajendra", "Rajesh", "Ramesh",
    "Sachin", "Sagar", "Samrat", "Sandeep", "Shiva",
    "Tarun", "Tenzin", "Tikka",
    "Uday", "Uma", "Umesha",
    "Vaibhav", "Vikram", "Vinay", "Vishal", "Vikas",
]

nepali_last_names = [
    "Acharya", "Adhikari", "Agrawal", "Aryal",
    "Bajaj", "Bhat", "Bhattacharya",
    "Chhetri", "Chopra", "Choudhary",
    "Dhakal", "Dhawan",
    "Giri", "Goel", "Gowda", "Gupta",
    "Iyer",
    "Jain", "Joshi",
    "Kadam", "Kalra",
    "Madan", "Mahajan",
    "Nair", "Nagarajan",
    "Patel", "Prabhakar",
    "Raina", "Raja", "Rajkumar",
    "Sada", "Sahoo", "Sharma",
    "Tagore", "Thapa",
    "Uddin",
    "Vaidya", "Vaishnav",
    "Yadav",
]

users_created = 0
user_profiles = []
django_users_to_create = []
user_profiles_to_create = []

with transaction.atomic():
    # Prepare all users first
    for idx in range(200):
        first_name = random.choice(nepali_first_names)
        last_name = random.choice(nepali_last_names)
        username = f"kathmandu_user_{idx + 1:03d}"
        email = f"kathmandu_user_{idx + 1:03d}@travelcompanion.test"
        
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
    all_django_users = DjangoUser.objects.filter(username__startswith='kathmandu_user_')
    print(f"  ✓ Found {all_django_users.count()} total Django users")
    
    for idx, django_user in enumerate(all_django_users):
        # Create profile if it doesn't exist
        user_profile, created = UserProfile.objects.get_or_create(
            user=django_user,
            defaults={
                'bio': f"Exploring Kathmandu and making new friends!",
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
# CREATE 20 TRIPS TO KATHMANDU
# ============================================================
print(f"\n✈️  Creating 20 Kathmandu trips with 10+ person groups...")

trips_created = 0
base_date = datetime.now() + timedelta(days=10)

with transaction.atomic():
    for trip_idx in range(20):
        # Select a creator from our users
        creator = random.choice(user_profiles)
        
        # Create trip
        trip = Trip.objects.create(
            title=f"{TRIP_THEMES[trip_idx % len(TRIP_THEMES)]} - Group {trip_idx + 1}",
            description=f"Join us for an amazing adventure in Kathmandu! "
                       f"We're looking for fellow travelers with diverse interests and backgrounds. "
                       f"Group size: 10+ people. Let's explore together!",
            creator=creator,
            destination=kathmandu_city,
            start_date=base_date + timedelta(days=random.randint(0, 60)),
            end_date=base_date + timedelta(days=random.randint(3, 15)),
            is_public=True,
            is_completed=False,
            trip_tags=random.choice([
                ["adventure", "cultural", "hiking"],
                ["temple", "spiritual", "meditation"],
                ["trekking", "nature", "photography"],
                ["party", "nightlife", "social"],
                ["budget", "backpacking", "exploration"],
            ]),
        )
        
        # Add 10-15 participants to this trip (ensuring diverse personalities)
        num_participants = random.randint(10, 15)
        
        # Get available users (exclude creator)
        available_users = [u for u in user_profiles if u != creator]
        selected_participants = random.sample(available_users, min(num_participants, len(available_users)))
        
        # Add them to the trip
        trip.participants.set(selected_participants)
        
        trips_created += 1
        
        print(f"  ✓ Trip {trip_idx + 1}/20: '{trip.title}' "
              f"({len(selected_participants)} participants)")

print(f"\n✓ Successfully created {trips_created} Kathmandu trips")

# ============================================================
# VERIFICATION & SUMMARY
# ============================================================
print("\n" + "=" * 70)
print("📊 VERIFICATION & SUMMARY")
print("=" * 70)

total_users = UserProfile.objects.filter(user__username__startswith='kathmandu_user_').count()
total_trips = Trip.objects.filter(destination=kathmandu_city, creator__user__username__startswith='kathmandu_user_').count()

print(f"\n✓ Total users created: {total_users}")
print(f"✓ Total Kathmandu trips created: {total_trips}")
print(f"✓ Average participants per trip: {user_profiles[0].joined_trips.count() if user_profiles else 0}")

# Show sample of users with their tags
print(f"\n📋 Sample Users with Personality Tags:")
sample_users = random.sample(user_profiles, min(5, len(user_profiles)))
for idx, user in enumerate(sample_users, 1):
    tags = [tag.name for tag in user.constraint_tags.all()]
    print(f"  {idx}. {user.user.first_name} {user.user.last_name}")
    print(f"     Tags: {', '.join(tags[:4])}")

# Show sample trips with participants
print(f"\n✈️  Sample Trips with Group Sizes:")
sample_trips = Trip.objects.filter(destination=kathmandu_city).order_by('-created_at')[:5]
for idx, trip in enumerate(sample_trips, 1):
    participant_count = trip.participants.count()
    print(f"  {idx}. {trip.title}")
    print(f"     Group Size: {participant_count} participants")

print("\n" + "=" * 70)
print("✅ TASK COMPLETED!")
print("=" * 70)
print(f"\n📍 All data ready for cosine similarity testing in Kathmandu!")
print(f"   • 200 users with diverse personality tags")
print(f"   • 20 Kathmandu trips with 10+ people each")
print(f"   • Tags cover: diet, lifestyle, values, age, gender, status")
print(f"\n💡 TIP: Test match scores in your Discover tab for varied similarity results")
