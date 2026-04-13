import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'travel_companion.settings'

# Override email backend BEFORE Django setup
from django.conf import settings
settings.EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'

import django
django.setup()

from datetime import datetime, timedelta
import random
from django.db import transaction
from apps.users.models import Interest, ConstraintTag, UserProfile
from apps.trips.models import Trip, City, TripExpenseBudget
from django.contrib.auth.models import User

print("=" * 70)
print("Creating 100 Nepalese Users with 2 Trips Each (FAST VERSION)")
print("=" * 70)

# Nepali Names
nepali_first = ["Aditya", "Amit", "Anuj", "Arjun", "Ashok", "Abhishek", "Arun", "Aman",
    "Bikram", "Bhoj", "Balkrishna", "Bhuwan", "Bhaskar", "Bimal", "Binod",
    "Chetan", "Chirag", "Chhabi", "Chandra", "Champa", "Chirendra",
    "Darshan", "Deepak", "Devendra", "Dawa", "Dipak", "Devi",
    "Eka", "Elu", "Eshan", "Fagil", "Freshan", "Farhan",
    "Gagan", "Ganesh", "Gendra", "Girish", "Gaurav", "Govardhan",
    "Hari", "Harihar", "Harendra", "Harish", "Hemanta", "Himal",
    "Indra", "Ishwar", "Irshad", "Ismail", "Jagat", "Jaya",
    "Jatan", "Jayendra", "Joshi", "Jeevan", "Kalyan", "Kamal",
    "Kapil", "Karun", "Karna", "Keshav", "Lal", "Lama",
    "Lodhi", "Lokendra", "Lekh", "Loknath", "Madan", "Mahendra",
    "Mangal", "Manish", "Manoj", "Mohan", "Nabin", "Naresh",
    "Narendra", "Navaraj", "Nayan", "Nikhil", "Om", "Oming",
    "Omand", "Prabhat", "Prabhakar", "Pradeep", "Pranav", "Prasad",
    "Prashant", "Rabi", "Raj", "Rajendra", "Rajesh", "Rajeev",
    "Ramesh", "Sachin", "Sagar", "Sai", "Sajit", "Samrat",
]

nepali_last = ["Acharya", "Adhikari", "Agrawal", "Akhtar", "Anand", "Aryal", "Arora", 
    "Bajaj", "Bajpai", "Bangia", "Bapna", "Bardhan", "Basu", "Bhagat", "Bhalla", "Bhat",
    "Bhattacharya", "Bhatnagar", "Bhimani", "Chandra", "Chandrasekar", "Chawla", "Chhetri",
    "Chopra", "Choudhary", "Chowdhury", "Daga", "Dasgupta", "Dhakal", "Dhawan", "Dixit",
    "Dugal", "Engineer", "Eriksen", "Giri", "Goel", "Gomberg", "Gopal", "Gowda",
    "Goyal", "Gupta", "Guruge", "Hada", "Haidari", "Hajari", "Haldar", "Halwai",
    "Hanafusa", "Hanna", "Iyer", "Jadhav", "Jain", "Jajoo", "Jalan", "Jalluri",
    "Jamkar", "Jander", "Jangid", "Kadam", "Kailey", "Kaji", "Kalani", "Kalita",
    "Kalra", "Kalyani", "Kammuri", "Lachman", "Lache", "Ladd", "Lade", "Ladha",
    "Lager", "Laha", "Lahiri", "Madan", "Made", "Magdala", "Mahabir", "Mahajan",
]

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

# Get data
print("\n📋 Loading data...")
cities = {}
for city_name in nepal_locations.keys():
    city, _ = City.objects.get_or_create(name=city_name, defaults={"country": "Nepal"})
    cities[city_name] = city

interests = list(Interest.objects.all()[:20])
constraint_tags = list(ConstraintTag.objects.all()[:8])
print(f"✓ Cities: {len(cities)}, Interests: {len(interests)}, Tags: {len(constraint_tags)}")

# Create users and trips
print("\n👥 Creating 100 users + 200 trips...")
users_to_create = []
profiles_to_create = []

with transaction.atomic():
    # Create users first
    for i in range(100):
        fname = random.choice(nepali_first)
        lname = random.choice(nepali_last)
        username = f"nepal_{i}_{fname[:3]}{lname[:3]}".lower()[:30]
        
        user = User(
            username=username,
            email=f"nepal{i}@test.com",
            first_name=fname,
            last_name=lname,
        )
        user.set_password('nepal123')
        users_to_create.append(user)
    
    print(f"  • Bulk creating {len(users_to_create)} users...")
    User.objects.bulk_create(users_to_create, ignore_conflicts=True)
    
    # Get created users
    nepal_users = list(User.objects.filter(username__startswith='nepal_'))
    print(f"  ✓ {len(nepal_users)} users created")
    
    # Create profiles
    for user in nepal_users:
        profile = UserProfile(
            user=user,
            bio=f'Nepali traveler',
            location=random.choice(list(nepal_locations.keys())),
            citizenship='Nepal',
            country='Nepal',
            travel_style=random.choice(['budget', 'luxury', 'adventure']),
            pace=random.choice(['relaxed', 'moderate', 'fast_paced']),
            accomodation_preference=random.choice(['hostel', 'hotel', 'inn', 'camping']),
            budget_level=random.randint(1, 10),
            adventure_level=random.randint(1, 10),
            social_level=random.randint(1, 10),
            public_profile=True,
        )
        profiles_to_create.append(profile)
    
    print(f"  • Bulk creating {len(profiles_to_create)} profiles...")
    UserProfile.objects.bulk_create(profiles_to_create, ignore_conflicts=True)
    print(f"  ✓ {len(profiles_to_create)} profiles created")
    
    # Add tags to profiles
    for profile in UserProfile.objects.filter(user__username__startswith='nepal_'):
        profile.interests.set(random.sample(interests, min(3, len(interests))))
        profile.constraint_tags.set(random.sample(constraint_tags, min(2, len(constraint_tags))))

# Create trips
print(f"\n✈️ Creating 200 trips...")
trip_count = 0
trips_to_create = []

with transaction.atomic():
    for idx, profile in enumerate(UserProfile.objects.filter(user__username__startswith='nepal_')):
        for trip_num in range(2):
            city = random.choice(list(cities.values()))
            start = datetime.now() + timedelta(days=random.randint(10, 60))
            
            trip = Trip(
                title=f"{city.name} Adventure",
                description=f"Trip to {city.name}",
                creator=profile,
                destination=city,
                start_date=start,
                end_date=start + timedelta(days=random.randint(3, 15)),
                is_public=random.choice([True, False]),
                is_completed=False,
                trip_tags=random.choice(trip_tags_list),
            )
            trips_to_create.append(trip)
            trip_count += 1
            
            if trip_count % 50 == 0:
                print(f"  • Preparing trip {trip_count}/200")
    
    print(f"  • Bulk creating {len(trips_to_create)} trips...")
    Trip.objects.bulk_create(trips_to_create)
    print(f"  ✓ {len(trips_to_create)} trips created")

print("\n" + "=" * 70)
print("✅ COMPLETE!")
print(f"   ✓ {UserProfile.objects.filter(user__username__startswith='nepal_').count()} Nepalese users")
print(f"   ✓ {Trip.objects.filter(creator__user__username__startswith='nepal_').count()} trips")
print("=" * 70)
