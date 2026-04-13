import os
import django
from datetime import datetime, timedelta
import random

# Disable email sending during population
os.environ['EMAIL_BACKEND'] = 'django.core.mail.backends.dummy.EmailBackend'

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_companion.settings')
django.setup()

# Disable signals during population
from django.db.models.signals import post_save
from django.contrib.auth.models import User as DjangoUser

from django.db import transaction
from apps.users.models import Interest, ConstraintTag, UserProfile
from apps.trips.models import Trip, City, TripExpenseBudget
from django.contrib.auth.models import User

print("=" * 60)
print("Creating 100 Nepalese Users with 2 Trips Each")
print("=" * 60)

# Nepali first and last names
nepali_first_names = [
    "Aditya", "Amit", "Anuj", "Arjun", "Ashok", "Abhishek", "Arun", "Aman",
    "Bikram", "Bhoj", "Balkrishna", "Bhuwan", "Bhaskar", "Bimal", "Binod",
    "Chetan", "Chirag", "Chhabi", "Chandra", "Champa", "Chirendra",
    "Darshan", "Deepak", "Devendra", "Dawa", "Dipak", "Devi",
    "Eka", "Elu", "Eshan",
    "Fagil", "Freshan", "Farhan",
    "Gagan", "Ganesh", "Gendra", "Girish", "Gaurav", "Govardhan",
    "Hari", "Harihar", "Harendra", "Harish", "Hemanta", "Himal",
    "Indra", "Ishwar", "Irshad", "Ismail",
    "Jagat", "Jaya", "Jatan", "Jayendra", "Joshi", "Jeevan",
    "Kalyan", "Kamal", "Kapil", "Karun", "Karna", "Keshav",
    "Lal", "Lama", "Lodhi", "Lokendra", "Lekh", "Loknath",
    "Madan", "Mahendra", "Mangal", "Manish", "Manoj", "Mohan",
    "Nabin", "Naresh", "Narendra", "Navaraj", "Nayan", "Nikhil",
    "Om", "Oming", "Omand",
    "Prabhat", "Prabhakar", "Pradeep", "Pranav", "Prasad", "Prashant",
    "Rabi", "Raj", "Rajendra", "Rajesh", "Rajeev", "Ramesh",
    "Sachin", "Sagar", "Sai", "Sajit", "Samrat", "Sandeep",
    "Tarak", "Tarun", "Tejendra", "Tenzin", "Tilo", "Tikal",
    "Uday", "Uma", "Umesha", "Umrao",
    "Vaibhav", "Vikram", "Vinay", "Vinesh", "Vishal", "Vishnu",
    "Yama", "Yaresh", "Yasharth", "Yogendra",
    "Zaman", "Zephix",
]

nepali_last_names = [
    "Acharya", "Adhikari", "Agrawal", "Akhtar", "Anand", "Aryal", "Arora",
    "Bajaj", "Bajpai", "Bangia", "Bapna", "Bardhan", "Basu", "Bhagat", "Bhalla", "Bhat", "Bhattacharya", "Bhatnagar", "Bhimani",
    "Chandra", "Chandrasekar", "Chawla", "Chhetri", "Chopra", "Choudhary", "Chowdhury",
    "Daga", "Dasgupta", "Dhakal", "Dhawan", "Dixit", "Dugal",
    "Engineer", "Eriksen",
    "Giri", "Goel", "Gomberg", "Gopal", "Gowda", "Goyal", "Gupta", "Guruge",
    "Hada", "Haidari", "Hajari", "Haldar", "Halwai", "Hanafusa", "Hanna",
    "Iyer",
    "Jadhav", "Jain", "Jajoo", "Jalan", "Jalluri", "Jamkar", "Jander", "Jangid",
    "Kadam", "Kailey", "Kaji", "Kalani", "Kalita", "Kalra", "Kalyani", "Kammuri",
    "Lachman", "Lache", "Ladd", "Lade", "Ladha", "Lager", "Laha", "Lahiri",
    "Madan", "Made", "Magdala", "Mahabir", "Mahajan", "Maharaja", "Maharshi",
    "Nagarajan", "Nagar", "Naidoo", "Nain", "Naini", "Nake", "Nambi", "Nambiar",
    "Pablani", "Pache", "Pacheco", "Pachner", "Pachpande", "Padhi", "Padmanabhan",
    "Raina", "Raja", "Rajagopalan", "Rajkumar", "Rajpurohit", "Rajwanshi",
    "Sada", "Sadangi", "Sadashiv", "Sadasivam", "Sadate", "Sadavarte", "Sade",
    "Tadi", "Tagore", "Tahbibi", "Tahernia", "Tajura", "Takahashi", "Takaoka",
    "Uddin", "Udeshi", "Udhawa", "Udigaonkar", "Udipi", "Udoh",
    "Vaidya", "Vaish", "Vaishnav", "Vaja", "Vakharia", "Vakil", "Vakshalimath",
    "Yadav", "Yadavar", "Yagich", "Yagi", "Yakabu", "Yakhni", "Yakimenko",
    "Zamora", "Zander", "Zanetis", "Zanker", "Zappa", "Zare",
]

# Nepal locations (cities & destinations)
nepal_locations = {
    "Kathmandu": {
        "destinations": ["Pashupatinath Temple", "Boudhanath Stupa", "Thamel District", "Patan Durbar Square"],
        "budget_range": (1000, 3000)
    },
    "Pokhara": {
        "destinations": ["Phewa Lake", "Annapurna Mountain View", "Davis Falls", "Peace Pagoda"],
        "budget_range": (800, 2500)
    },
    "Kathmandu": {
        "destinations": ["Swayambhunath", "Garden of Dreams", "Narayanhiti Palace"],
        "budget_range": (1000, 2500)
    },
    "Chitwan": {
        "destinations": ["Chitwan National Park", "Jungle Safari", "Rapti River"],
        "budget_range": (1200, 3500)
    },
    "Nagarkot": {
        "destinations": ["Himalayan Views", "Sunrise Point", "Local Villages"],
        "budget_range": (600, 2000)
    },
    "Bhaktapur": {
        "destinations": ["Bhaktapur Durbar Square", "Pottery Square", "Tachupal Tole"],
        "budget_range": (700, 2200)
    },
    "Janakpur": {
        "destinations": ["Janaki Mandir Temple", "Ganga Sagar Pool", "Ram Navami Festival"],
        "budget_range": (500, 1800)
    },
    "Nepalgunj": {
        "destinations": ["Babai River", "Bardiya National Park", "Karnali River"],
        "budget_range": (700, 2400)
    },
    "Ilam": {
        "destinations": ["Tea Gardens", "Kahlo Mountain", "Antu Danda"],
        "budget_range": (600, 1900)
    },
    "Gorkha": {
        "destinations": ["Gorakhnath Cave", "Manakamana Temple", "Amar Narayan Temple"],
        "budget_range": (800, 2300)
    },
    "Bandipur": {
        "destinations": ["Bandipur Bazaar", "Siddha Cave", "Thani Mai Temple"],
        "budget_range": (700, 2100)
    },
    "Dhulikhel": {
        "destinations": ["Namobuddha", "Ainkhu River", "Indreshwar Mahadev Temple"],
        "budget_range": (600, 2000)
    },
}

# Trip tags and interests to vary
trip_tags_list = [
    ["hiking", "adventure", "budget"],
    ["trekking", "mountain", "scenic"],
    ["cultural", "temple", "exploration"],
    ["nature", "wildlife", "photography"],
    ["spiritual", "meditation", "peace"],
    ["food", "cooking", "local"],
    ["nightlife", "city", "social"],
    ["beach", "water", "relaxation"],
    ["adventure", "extreme", "thrill"],
    ["family", "kids", "relaxed"],
    ["luxury", "comfort", "experience"],
    ["eco-friendly", "sustainable", "nature"],
    ["art", "museum", "culture"],
    ["coffee", "local", "casual"],
    ["yoga", "wellness", "retreat"],
]

constraint_tags_to_use = [
    "Vegetarian", "Non-vegetarian", "Non-smoker", "Early Riser",
    "Budget Conscious", "Eco-conscious", "25-35", "Fitness Focused"
]

# Get or create cities
print("\n📍 Creating/Getting Nepalese Cities...")
cities = {}
for city_name in nepal_locations.keys():
    city, created = City.objects.get_or_create(
        name=city_name,
        defaults={"country": "Nepal"}
    )
    cities[city_name] = city
    if created:
        print(f"  ✓ Created city: {city_name}")

print(f"\n✓ Total cities: {len(cities)}")

# Get interests and constraint tags
interests = Interest.objects.all()
constraint_tags = ConstraintTag.objects.filter(name__in=constraint_tags_to_use)

if not interests.exists():
    print("❌ No interests found! Please run populate_data.py first")
    exit()

if not constraint_tags.exists():
    print("❌ No constraint tags found! Please run populate_data.py first")
    exit()

print(f"✓ Found {interests.count()} interests")
print(f"✓ Found {constraint_tags.count()} constraint tags")

# Create 100 users
print("\n👥 Creating 100 Nepalese Users...")
created_users = []

# Disconnect the post_save signal to avoid email sending
from apps.users.signals import create_user_profile
post_save.disconnect(create_user_profile, sender=DjangoUser)

with transaction.atomic():
    for i in range(100):
        first_name = random.choice(nepali_first_names)
        last_name = random.choice(nepali_last_names)
        username = f"{first_name.lower()}_{last_name.lower()}_{i}".replace(" ", "_")[:30]
        email = f"nepal_user_{i}@travelchat.com"
        
        # Create or get user
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
            }
        )
        
        if created:
            user.set_password('nepal123')
            user.save()
        
        # Create or update profile
        profile, _ = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'bio': f'Traveler from Nepal loves exploring {random.choice(list(nepal_locations.keys()))}',
                'location': random.choice(list(nepal_locations.keys())),
                'citizenship': 'Nepal',
                'country': 'Nepal',
                'travel_style': random.choice(['budget', 'luxury', 'adventure']),
                'pace': random.choice(['relaxed', 'moderate', 'fast_paced']),
                'accomodation_preference': random.choice(['hostel', 'hotel', 'inn', 'camping']),
                'budget_level': random.randint(1, 10),
                'adventure_level': random.randint(1, 10),
                'social_level': random.randint(1, 10),
                'public_profile': True,
            }
        )
        
        # Add random interests (3-5)
        num_interests = random.randint(3, 5)
        selected_interests = random.sample(list(interests), min(num_interests, interests.count()))
        profile.interests.set(selected_interests)
        
        # Add random constraint tags (2-3)
        num_tags = random.randint(2, 3)
        selected_tags = random.sample(list(constraint_tags), min(num_tags, constraint_tags.count()))
        profile.constraint_tags.set(selected_tags)
        
        created_users.append(profile)
        
        if (i + 1) % 20 == 0:
            print(f"  ✓ Created {i + 1} users")

# Reconnect the signal
post_save.connect(create_user_profile, sender=DjangoUser)

print(f"\n✓ Total users created: {len(created_users)}")

# Create 2 trips for each user
print("\n✈️ Creating 2 trips for each user...")
trip_count = 0

with transaction.atomic():
    for idx, user_profile in enumerate(created_users):
        for trip_num in range(2):
            city = random.choice(list(cities.values()))
            destination_name = random.choice(nepal_locations[city.name]["destinations"])
            
            start_date = datetime.now() + timedelta(days=random.randint(10, 60))
            end_date = start_date + timedelta(days=random.randint(3, 15))
            
            trip_title = f"Epic {city.name} Adventure #{trip_num + 1}"
            trip_desc = f"Join me for an amazing trip to {destination_name}! Looking for fellow travelers who enjoy {random.choice(['hiking', 'cultural experiences', 'food tours', 'photography', 'relaxation'])}."
            
            trip = Trip.objects.create(
                title=trip_title,
                description=trip_desc,
                creator=user_profile,
                destination=city,
                start_date=start_date,
                end_date=end_date,
                is_public=random.choice([True, False]),
                is_completed=False,
            )
            
            # Add constraint tags to trip
            trip_constraint_tags = random.sample(
                list(ConstraintTag.objects.all()),
                min(random.randint(1, 3), ConstraintTag.objects.count())
            )
            trip.constraint_tags.set(trip_constraint_tags)
            
            # Add trip tags (JSON)
            trip.trip_tags = random.choice(trip_tags_list)
            trip.save()
            
            # Create budget entries for the trip
            budget_min, budget_max = nepal_locations[city.name]["budget_range"]
            budget_categories = [
                ("Transportation", random.randint(budget_min // 4, budget_max // 4)),
                ("Accommodation", random.randint(budget_min // 3, budget_max // 3)),
                ("Food", random.randint(budget_min // 4, budget_max // 4)),
                ("Activities", random.randint(budget_min // 5, budget_max // 5)),
            ]
            
            for category, amount in budget_categories:
                TripExpenseBudget.objects.create(
                    trip=trip,
                    category=category,
                    amount=amount
                )
            
            trip_count += 1
            
            if (trip_count) % 50 == 0:
                print(f"  ✓ Created {trip_count} trips")

print(f"\n✓ Total trips created: {trip_count}")
print("\n" + "=" * 60)
print("✅ Successfully created:")
print(f"   • 100 Nepalese users")
print(f"   • {trip_count} trips (2 per user)")
print(f"   • {trip_count * 4} budget entries")
print("=" * 60)
