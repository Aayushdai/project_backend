"""
Management command to populate 100 Nepali travel buddies with realistic locations, addresses, and tags.
For testing the cosine similarity matching algorithm.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.users.models import Interest, ConstraintTag, UserProfile
import random
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Create 100 Nepali users with random addresses, locations, and constraint tags for algorithm testing'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🇳🇵 Starting Nepali User Population...'))

        # ═══════════════════════════════════════════════════════════════════════════
        # REALISTIC NEPALESE LOCATIONS & ADDRESSES
        # ═══════════════════════════════════════════════════════════════════════════

        NEPAL_LOCATIONS = {
            # Kathmandu Valley
            'Kathmandu': [
                'Thamel, Kathmandu', 'Bhaktapur, Kathmandu Valley', 'Patan, Lalitpur',
                'Swayambhunath, Kathmandu', 'Boudhanath, Kathmandu', 'Pashupatinath, Kathmandu',
                'New Baneshwor, Kathmandu', 'Chabahil, Kathmandu', 'Baluwatar, Kathmandu',
                'Lazimpat, Kathmandu', 'Naxal, Kathmandu', 'Mahagonj, Kathmandu'
            ],
            # Pokhara Region
            'Pokhara': [
                'Lakeside, Pokhara', 'Damside, Pokhara', 'Sarankot, Pokhara',
                'Fewa, Pokhara', 'Ardak Tal, Pokhara', 'Naya Baneshwor, Pokhara',
                'Ranikhad, Pokhara', 'Bindabasini, Pokhara', 'Dhikur Pokhari, Pokhara'
            ],
            # Himalayan Towns
            'Mountain Region': [
                'Namche Bazaar, Sagarmatha', 'Lukla, Solukhumbu', 'Kathmandu Gateway, Everest Trek',
                'Ilam District (Tea Gardens)', 'Ilam Bazaar', 'Gorkha, Gorkha District',
                'Janakpur, Mithila Region', 'Birgunj, Parsa', 'Biratnagar, Morang'
            ],
            # Western Region
            'Western Nepal': [
                'Nepalgunj, Banke', 'Butwal, Rupandehi', 'Dhulikhel, Kavre', 'Narayanghat, Chitwan'
            ],
            # Eastern Region
            'Eastern Nepal': [
                'Itahari, Sunsari', 'Damak, Jhapa', 'Dharan, Sunsari', 'Biratnagar, Morang'
            ],
            # Adventure Towns
            'Adventure Hotspots': [
                'Bhaktapur (Old City)', 'Nagarkot, Bhaktapur', 'Changunarayan, Bhaktapur',
                'Shyangboche, Sagarmatha', 'Ghorepani, Myagdi', 'Bandipur, Tanahun',
                'Nuwakot, Nuwakot District', 'Dhulikhel, Ancient City'
            ]
        }

        # ═══════════════════════════════════════════════════════════════════════════
        # INTEREST COMBINATIONS FOR DIVERSE USER PROFILES
        # ═══════════════════════════════════════════════════════════════════════════

        INTEREST_PERSONAS = {
            'Adventure Seeker': ['Hiking', 'Rock Climbing', 'Mountains', 'Adventure Sports', 'Wildlife Watching'],
            'Cultural Explorer': ['Cultural Immersion', 'Museum Visits', 'Local Food Tours', 'Cities'],
            'Food Lover': ['Local Food Tours', 'Cooking', 'Cities', 'Cultural Immersion'],
            'Nature Photographer': ['Photography', 'Mountains', 'Forests', 'Wildlife Watching', 'Nature'],
            'Budget Backpacker': ['Cycling', 'Beach Activities', 'Budget Conscious', 'Hostels'],
            'Luxury Traveler': ['Beaches', 'Nightlife', 'Hotel Stays', 'Cities'],
            'Spiritual Soul': ['Yoga', 'Mountains', 'Cultural Immersion', 'Meditation'],
            'Sports Enthusiast': ['Adventure Sports', 'Scuba Diving', 'Surfing', 'Cycling'],
            'Urban Explorer': ['Cities', 'Nightlife', 'Museum Visits', 'Local Food Tours'],
            'Nature Lover': ['Forests', 'Mountains', 'Beaches', 'Wildlife Watching'],
        }

        # ═══════════════════════════════════════════════════════════════════════════
        # CONSTRAINT TAG COMBINATIONS FOR REALISTIC MATCHING
        # ═══════════════════════════════════════════════════════════════════════════

        TAG_COMBINATIONS = [
            # Constraint sets that work well together
            ['Vegetarian', 'Non-Smoker', 'Eco-conscious'],
            ['Non-Vegetarian', 'Non-Smoker', 'Fitness Focused'],
            ['Vegetarian', 'Social Drinker', 'Budget Conscious'],
            ['Non-Vegetarian', 'Smoker', 'Night Owl'],
            ['Non-Vegetarian', 'Social Drinker', 'Early Riser'],
            ['Vegetarian', 'Non-Smoker', 'Budget Conscious'],
            ['Non-Vegetarian', 'Social Drinker', 'Luxury Lover'],
            ['Vegan', 'Non-Smoker', 'Eco-conscious'],
            ['Halal', 'Non-Smoker', 'Budget Conscious'],
            ['Vegetarian', 'Social Drinker', 'Eco-conscious'],
            ['Non-Vegetarian', 'Non-Smoker', 'Adventure Seeker'],
            ['Vegetarian', 'Non-Smoker', 'Meditation Focused'],
            ['Non-Vegetarian', 'Social Drinker', 'Party Person'],
            ['Vegetarian', 'Non-Smoker', 'Fitness Focused'],
            ['Non-Vegetarian', 'Social Drinker', 'Cultural Explorer'],
        ]

        AGE_RANGES = ['18-25', '25-35', '35-50', '50+']

        # ═══════════════════════════════════════════════════════════════════════════
        # NEPALESE NAMES FOR REALISTIC PROFILES
        # ═══════════════════════════════════════════════════════════════════════════

        NEPALI_FIRST_NAMES = [
            'Arun', 'Bishan', 'Chandra', 'Deepak', 'Eshan', 'Faisal', 'Gaurav', 'Hari',
            'Ishan', 'Jaya', 'Karan', 'Lokesh', 'Mahesh', 'Narayan', 'Omprakash', 'Prakash',
            'Qasim', 'Rajesh', 'Suresh', 'Tara', 'Uday', 'Vikram', 'Wali', 'Xavier',
            'Yogesh', 'Zaman', 'Anita', 'Binita', 'Chhaya', 'Deepika', 'Esha', 'Farida',
            'Gita', 'Hasini', 'Isha', 'Jyoti', 'Kavya', 'Lakshmi', 'Mamta', 'Neha',
        ]

        NEPALI_LAST_NAMES = [
            'Khadka', 'Rai', 'Sherpa', 'Sharma', 'Poudel', 'Adhikari', 'Thapa', 'Gurung',
            'Tamang', 'Limboo', 'Aadhikari', 'Baniya', 'Basnet', 'Bhandari', 'Bhattarai',
            'Dahal', 'Ghayal', 'Ghimire', 'Joshi', 'Kini', 'Koirala', 'Maitri',
        ]

        # Get or create interests and tags
        interests_dict = {obj.name: obj for obj in Interest.objects.all()}
        tags_dict = {obj.name: obj for obj in ConstraintTag.objects.all()}

        if not interests_dict:
            self.stdout.write(self.style.ERROR('❌ No interests found in database. Run populate_test_data first.'))
            return

        if not tags_dict:
            self.stdout.write(self.style.ERROR('❌ No constraint tags found in database. Run populate_test_data first.'))
            return

        # ═══════════════════════════════════════════════════════════════════════════
        # CREATE 100 USERS
        # ═══════════════════════════════════════════════════════════════════════════

        created_count = 0
        skipped_count = 0

        for i in range(1, 101):
            username = f'nepal_traveler_{i}'
            
            if User.objects.filter(username=username).exists():
                skipped_count += 1
                continue

            # Random names
            first_name = random.choice(NEPALI_FIRST_NAMES)
            last_name = random.choice(NEPALI_LAST_NAMES)

            # Create user
            user = User.objects.create_user(
                username=username,
                email=f'{username}@travelsathi.com',
                first_name=first_name,
                last_name=last_name,
                password='testpass123'
            )

            # Random location from Nepal
            region = random.choice(list(NEPAL_LOCATIONS.keys()))
            location = random.choice(NEPAL_LOCATIONS[region])

            # Create profile with realistic Nepal address
            district = location.split(',')[-1] if ',' in location else location
            address = f'{random.randint(100, 9999)} {random.choice(["Siddhartha", "Prithvi", "Tribhuvan", "Arun"])}, {location}'

            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'bio': f'Travel enthusiast from {location}. Love exploring Nepal and beyond.',
                    'location': location,
                    'address': address,
                    'city': location.split(',')[0],
                    'country': 'Nepal',
                    'zip_code': f'KTM{random.randint(1000, 9999)}',
                    'dob': datetime.now() - timedelta(days=random.randint(7300, 18250)),  # Age 20-50
                    'gender': random.choice(['Male', 'Female']),
                    'citizenship': 'Nepal',
                    'phone': f'+977-{random.randint(1000000000, 9999999999)}',
                    'travel_style': random.choice(['budget', 'luxury', 'adventure']),
                    'pace': random.choice(['relaxed', 'moderate', 'fast_paced']),
                    'accomodation_preference': random.choice(['hostel', 'hotel', 'inn', 'camping']),
                    'budget_level': random.randint(1, 10),
                    'adventure_level': random.randint(1, 10),
                    'social_level': random.randint(1, 10),
                }
            )

            # Assign interests based on persona
            persona = random.choice(list(INTEREST_PERSONAS.keys()))
            interest_names = INTEREST_PERSONAS[persona]
            for interest_name in interest_names:
                if interest_name in interests_dict:
                    profile.interests.add(interests_dict[interest_name])

            # Assign constraint tags (2-3 tags + age range)
            tags_to_assign = random.choice(TAG_COMBINATIONS)
            age_range = random.choice(AGE_RANGES)
            
            for tag_name in tags_to_assign + [age_range]:
                if tag_name in tags_dict:
                    profile.constraint_tags.add(tags_dict[tag_name])

            created_count += 1

            if created_count % 10 == 0:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created {created_count} users...')
                )

        # ═══════════════════════════════════════════════════════════════════════════
        # SUMMARY
        # ═══════════════════════════════════════════════════════════════════════════

        self.stdout.write(
            self.style.SUCCESS(f'\n✅ Successfully created {created_count} Nepali travel buddies!')
        )
        self.stdout.write(
            self.style.WARNING(f'⏭️  Skipped {skipped_count} existing users')
        )
        self.stdout.write(
            self.style.SUCCESS(f'\n📊 Total Users in System: {User.objects.filter(userprofile__country="Nepal").count()}')
        )
        self.stdout.write(
            self.style.SUCCESS(f'📊 Total Profiles: {UserProfile.objects.count()}')
        )
        self.stdout.write(
            self.style.SUCCESS(
                '\n✨ Your cosine similarity algorithm can now match travel buddies accurately! 🚀'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                '\n💡 Features tested:\n'
                '   • 100 diverse user personas\n'
                '   • Realistic Nepali locations & addresses\n'
                '   • Varied constraint tags for strict matching\n'
                '   • Random travel preferences\n'
                '   • Ages 20-50 with varied interests\n'
            )
        )
