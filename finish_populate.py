import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_companion.settings')
django.setup()

from apps.users.models import Interest, ConstraintTag, UserProfile, Match, UserLoginHistory
from django.contrib.auth.models import User
from django.utils.timezone import now
from datetime import timedelta
import random

print("Populating remaining test data...")

# Get existing interests and constraint tags
interests = {obj.name: obj for obj in Interest.objects.all()}
constraint_tags = {obj.name: obj for obj in ConstraintTag.objects.all()}

# Define users to create
test_users_data = [
    {
        'username': 'ravi_budgetpacker',
        'email': 'ravi@travelsathi.com',
        'first_name': 'Ravi',
        'last_name': 'Kumar',
        'password': 'testpass123',
        'profile': {
            'bio': 'Budget traveler exploring the world on a shoestring. Long-term nomad.',
            'location': 'Bangalore, India',
            'preferred_destinations': 'Southeast Asia, Central America, Eastern Europe',
            'travel_style': 'budget',
            'pace': 'fast_paced',
            'accomodation_preference': 'hostel',
            'phone': '+91-80-2222-3333',
            'dob': '1998-06-12',
            'gender': 'Male',
            'citizenship': 'India',
            'budget_level': 9,
            'adventure_level': 8,
            'social_level': 9,
            'interests': ['Cycling', 'Cities', 'Local Food Tours'],
            'constraints': ['Vegetarian', 'Budget Conscious', '18-25'],
        }
    },
    {
        'username': 'lisa_yoga',
        'email': 'lisa@travelsathi.com',
        'first_name': 'Lisa',
        'last_name': 'Anderson',
        'password': 'testpass123',
        'profile': {
            'bio': 'Yoga instructor seeking wellness retreats and peaceful destinations.',
            'location': 'Bali, Indonesia',
            'preferred_destinations': 'India, Thailand, Peru, Costa Rica',
            'travel_style': 'luxury',
            'pace': 'relaxed',
            'accomodation_preference': 'hotel',
            'phone': '+62-361-999-8888',
            'dob': '1990-09-18',
            'gender': 'Female',
            'citizenship': 'USA',
            'budget_level': 7,
            'adventure_level': 5,
            'social_level': 7,
            'interests': ['Yoga', 'Beaches', 'Cultural Immersion'],
            'constraints': ['Vegetarian', 'Non-smoker', 'Eco-conscious'],
        }
    },
]

created_users = {}
for user_data in test_users_data:
    username = user_data['username']
    if not User.objects.filter(username=username).exists():
        user = User.objects.create_user(
            username=username,
            email=user_data['email'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            password=user_data['password'],
        )
        
        profile_data = user_data['profile']
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'bio': profile_data['bio'],
                'location': profile_data['location'],
                'preferred_destinations': profile_data['preferred_destinations'],
                'travel_style': profile_data['travel_style'],
                'pace': profile_data['pace'],
                'accomodation_preference': profile_data['accomodation_preference'],
                'phone': profile_data['phone'],
                'dob': profile_data['dob'],
                'gender': profile_data['gender'],
                'citizenship': profile_data['citizenship'],
                'budget_level': profile_data['budget_level'],
                'adventure_level': profile_data['adventure_level'],
                'social_level': profile_data['social_level'],
                'status': 'approved',
            }
        )
        
        for interest_name in profile_data.get('interests', []):
            if interest_name in interests:
                profile.interests.add(interests[interest_name])
        
        for constraint_name in profile_data.get('constraints', []):
            if constraint_name in constraint_tags:
                profile.constraint_tags.add(constraint_tags[constraint_name])
        
        created_users[username] = user
        print(f'  ✓ Created User: {user_data["first_name"]} {user_data["last_name"]} ({username})')

print(f"\n✅ Data Population Complete!")
print(f'  • Interests: {Interest.objects.count()}')
print(f'  • Constraint Tags: {ConstraintTag.objects.count()}')
print(f'  • User Profiles: {UserProfile.objects.count()}')
print(f'  • Matches: {Match.objects.count()}')
print(f'  • Login History Records: {UserLoginHistory.objects.count()}')
