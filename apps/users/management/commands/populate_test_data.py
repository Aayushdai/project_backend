from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils.timezone import now
from datetime import timedelta
from apps.users.models import Interest, ConstraintTag, UserProfile, Match, UserLoginHistory
import random

class Command(BaseCommand):
    help = 'Populate test data for Interests, Constraint Tags, User Profiles, Matches, and Login History'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting data population...'))

        # 1. Create Interests
        self.stdout.write('Creating Interests...')
        interests_data = [
            # Activities
            ('Hiking', 'Outdoor physical activity', 'activity'),
            ('Photography', 'Capturing moments and landscapes', 'activity'),
            ('Cooking', 'Learning local cuisines', 'activity'),
            ('Scuba Diving', 'Underwater exploration', 'activity'),
            ('Rock Climbing', 'Adventure sports', 'activity'),
            ('Yoga', 'Wellness and mindfulness', 'activity'),
            ('Cycling', 'Bike tours and exploration', 'activity'),
            ('Surfing', 'Water sports', 'activity'),
            
            # Destinations
            ('Mountains', 'Alpine regions and peaks', 'destination'),
            ('Beaches', 'Coastal areas', 'destination'),
            ('Cities', 'Urban exploration', 'destination'),
            ('Deserts', 'Arid landscapes', 'destination'),
            ('Islands', 'Island hopping', 'destination'),
            ('Forests', 'Jungle and woodland areas', 'destination'),
            
            # Experiences
            ('Cultural Immersion', 'Deep cultural experiences', 'experience'),
            ('Local Food Tours', 'Tasting authentic cuisine', 'experience'),
            ('Museum Visits', 'Art and history', 'experience'),
            ('Nightlife', 'Clubs, bars, and social scene', 'experience'),
            ('Wildlife Watching', 'Animal encounters', 'experience'),
            ('Adventure Sports', 'Thrill-seeking activities', 'experience'),
        ]
        
        interests = {}
        for name, desc, category in interests_data:
            obj, created = Interest.objects.get_or_create(
                name=name,
                defaults={'description': desc, 'category': category}
            )
            interests[name] = obj
            if created:
                self.stdout.write(f'  ✓ Created Interest: {name}')

        # 2. Create Constraint Tags
        self.stdout.write('Creating Constraint Tags...')
        constraint_data = [
            # Diet
            ('Vegetarian', 'diet'),
            ('Vegan', 'diet'),
            ('Non-vegetarian', 'diet'),
            ('Halal', 'diet'),
            
            # Lifestyle
            ('Non-smoker', 'lifestyle'),
            ('Smoker', 'lifestyle'),
            ('Early Riser', 'lifestyle'),
            ('Night Owl', 'lifestyle'),
            ('Fitness Focused', 'lifestyle'),
            
            # Values
            ('Eco-conscious', 'values'),
            ('Budget Conscious', 'values'),
            ('Luxury Lover', 'values'),
            ('Minimalist', 'values'),
            
            # Age Range
            ('18-25', 'age_range'),
            ('25-35', 'age_range'),
            ('35-50', 'age_range'),
            ('50+', 'age_range'),
        ]
        
        constraint_tags = {}
        for name, category in constraint_data:
            obj, created = ConstraintTag.objects.get_or_create(
                name=name,
                category=category,
                defaults={'description': f'{category.title()}: {name}'}
            )
            constraint_tags[name] = obj
            if created:
                self.stdout.write(f'  ✓ Created Constraint Tag: {category.title()} - {name}')

        # 3. Create Test Users with Profiles
        self.stdout.write('Creating Test Users and Profiles...')
        
        test_users_data = [
            {
                'username': 'alex_traveler',
                'email': 'alex@travelsathi.com',
                'first_name': 'Alex',
                'last_name': 'Johnson',
                'password': 'testpass123',
                'profile': {
                    'bio': 'Adventurous traveler looking for hiking buddies and cultural experiences.',
                    'location': 'Colorado, USA',
                    'preferred_destinations': 'Mountains, Himalayas, Swiss Alps',
                    'travel_style': 'adventure',
                    'pace': 'moderate',
                    'accomodation_preference': 'hostel',
                    'phone': '+1-555-0101',
                    'dob': '1995-03-15',
                    'gender': 'Male',
                    'citizenship': 'USA',
                    'budget_level': 7,
                    'adventure_level': 9,
                    'social_level': 8,
                    'interests': ['Hiking', 'Photography', 'Mountains', 'Adventure Sports', 'Cultural Immersion'],
                    'constraints': ['Non-smoker', 'Fitness Focused', '25-35'],
                }
            },
            {
                'username': 'priya_explorer',
                'email': 'priya@travelsathi.com',
                'first_name': 'Priya',
                'last_name': 'Singh',
                'password': 'testpass123',
                'profile': {
                    'bio': 'Food lover and culture enthusiast. Love exploring local cuisines and traditions.',
                    'location': 'Delhi, India',
                    'preferred_destinations': 'Southeast Asia, Mediterranean, India',
                    'travel_style': 'luxury',
                    'pace': 'relaxed',
                    'accomodation_preference': 'hotel',
                    'phone': '+91-98765-43210',
                    'dob': '1994-07-22',
                    'gender': 'Female',
                    'citizenship': 'India',
                    'budget_level': 8,
                    'adventure_level': 6,
                    'social_level': 9,
                    'interests': ['Cooking', 'Local Food Tours', 'Museum Visits', 'Cultural Immersion', 'Cities'],
                    'constraints': ['Vegetarian', 'Non-smoker', '25-35'],
                }
            },
            {
                'username': 'marco_beach',
                'email': 'marco@travelsathi.com',
                'first_name': 'Marco',
                'last_name': 'Costa',
                'password': 'testpass123',
                'profile': {
                    'bio': 'Beach and water sports enthusiast. Always up for diving and surfing adventures.',
                    'location': 'Rio de Janeiro, Brazil',
                    'preferred_destinations': 'Caribbean, Bali, Thailand, Australia',
                    'travel_style': 'adventure',
                    'pace': 'fast_paced',
                    'accomodation_preference': 'hostel',
                    'phone': '+55-21-99999-8888',
                    'dob': '1996-11-05',
                    'gender': 'Male',
                    'citizenship': 'Brazil',
                    'budget_level': 6,
                    'adventure_level': 10,
                    'social_level': 8,
                    'interests': ['Surfing', 'Scuba Diving', 'Beaches', 'Adventure Sports', 'Nightlife'],
                    'constraints': ['Non-smoker', 'Early Riser', '25-35'],
                }
            },
            {
                'username': 'emma_photographer',
                'email': 'emma@travelsathi.com',
                'first_name': 'Emma',
                'last_name': 'Wilson',
                'password': 'testpass123',
                'profile': {
                    'bio': 'Professional photographer documenting travel stories. Love nature and wildlife.',
                    'location': 'London, UK',
                    'preferred_destinations': 'Africa, Iceland, New Zealand, Tasmania',
                    'travel_style': 'adventure',
                    'pace': 'moderate',
                    'accomodation_preference': 'camping',
                    'phone': '+44-20-7946-0958',
                    'dob': '1992-01-30',
                    'gender': 'Female',
                    'citizenship': 'UK',
                    'budget_level': 7,
                    'adventure_level': 8,
                    'social_level': 7,
                    'interests': ['Photography', 'Wildlife Watching', 'Forests', 'Mountains', 'Nature'],
                    'constraints': ['Non-smoker', 'Eco-conscious', '35-50'],
                }
            },
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
                    'interests': ['Cycling', 'Budget Conscious', 'Cities', 'Local Food Tours', 'Hostels'],
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
                    'bio': 'Yoga instructor seeking wellness retreats and peaceful destinations. Mindfulness focused.',
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
                    'interests': ['Yoga', 'Beaches', 'Cultural Immersion', 'Wellness', 'Meditation'],
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
                
                # Add interests
                for interest_name in profile_data['interests']:
                    if interest_name in interests:
                        profile.interests.add(interests[interest_name])
                
                # Add constraint tags
                for constraint_name in profile_data['constraints']:
                    if constraint_name in constraint_tags:
                        profile.constraint_tags.add(constraint_tags[constraint_name])
                
                created_users[username] = user
                self.stdout.write(f'  ✓ Created User: {user_data["first_name"]} {user_data["last_name"]} ({username})')
            else:
                created_users[username] = User.objects.get(username=username)

        # 4. Create Matches
        self.stdout.write('Creating Matches...')
        users_list = list(created_users.values())
        matches_created = 0
        
        if len(users_list) >= 2:
            for i in range(len(users_list) - 1):
                user1 = users_list[i]
                user2 = users_list[i + 1]
                
                similarity_score = round(random.uniform(0.65, 0.99), 2)
                status = random.choice(['pending', 'accepted'])
                
                match, created = Match.objects.get_or_create(
                    user1=user1,
                    user2=user2,
                    defaults={
                        'similarity_score': similarity_score,
                        'status': status,
                    }
                )
                if created:
                    matches_created += 1
                    self.stdout.write(f'  ✓ Created Match: {user1.username} ↔ {user2.username} (Score: {similarity_score})')

        # 5. Create Login History
        self.stdout.write('Creating Login History...')
        login_history_count = 0
        
        for user in users_list:
            # Create 5 login records for each user
            for i in range(5):
                login_time = now() - timedelta(days=random.randint(1, 30), hours=random.randint(0, 23))
                login_history, created = UserLoginHistory.objects.get_or_create(
                    user=user,
                    login_time=login_time,
                    defaults={
                        'ip_address': f'192.168.{random.randint(0, 255)}.{random.randint(1, 254)}',
                        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    }
                )
                if created:
                    login_history_count += 1

        if login_history_count > 0:
            self.stdout.write(f'  ✓ Created {login_history_count} Login History records')

        # Summary
        self.stdout.write(self.style.SUCCESS('\n✅ Data Population Complete!'))
        self.stdout.write(f'  • Interests: {len(interests)}')
        self.stdout.write(f'  • Constraint Tags: {len(constraint_tags)}')
        self.stdout.write(f'  • Users Created: {len(created_users)}')
        self.stdout.write(f'  • Matches Created: {matches_created}')
        self.stdout.write(f'  • Login History Records: {login_history_count}')
