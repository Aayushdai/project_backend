from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.users.models import UserProfile, Interest, ConstraintTag
from datetime import datetime
import random


class Command(BaseCommand):
    help = 'Populate users with travel interests and constraint tags for cosine similarity matching'

    def handle(self, *args, **options):
        # Create Interest categories
        interests_data = {
            'activity': [
                ('Hiking', 'Outdoor hiking and trekking'),
                ('Photography', 'Travel photography'),
                ('Cultural Tours', 'Exploring local culture'),
                ('Beach Activities', 'Beach and water sports'),
                ('Nightlife', 'Exploring nightlife and bars'),
                ('Food & Cuisine', 'Trying local cuisines'),
                ('Adventure Sports', 'Extreme sports and adventures'),
                ('Museum Visits', 'Visiting museums and galleries'),
                ('Wildlife Watching', 'Observing animals in nature'),
                ('Meditation & Yoga', 'Wellness and spiritual practices'),
            ],
            'destination': [
                ('Mountains', 'High altitude destinations'),
                ('Beaches', 'Coastal destinations'),
                ('Cities', 'Urban exploration'),
                ('Rural Areas', 'Countryside and villages'),
                ('Islands', 'Island destinations'),
                ('Deserts', 'Desert destinations'),
                ('Jungles', 'Tropical forests'),
                ('Historical Sites', 'Places with historical significance'),
            ],
            'experience': [
                ('Budget Travel', 'Traveling on a tight budget'),
                ('Luxury Travel', 'High-end travel experiences'),
                ('Solo Travel', 'Traveling alone'),
                ('Group Travel', 'Traveling with groups'),
                ('Family Travel', 'Traveling with family'),
                ('Backpacking', 'Backpacking adventures'),
            ]
        }

        # Create Interest objects
        created_interests = {}
        for category, interests_list in interests_data.items():
            for name, description in interests_list:
                interest, created = Interest.objects.get_or_create(
                    name=name,
                    defaults={'description': description, 'category': category}
                )
                created_interests[name] = interest
                if created:
                    self.stdout.write(f"✅ Created Interest: {name} ({category})")

        # Create Constraint Tags
        constraint_data = {
            'diet': [
                ('Vegetarian', 'Vegetarian diet preference'),
                ('Vegan', 'Vegan diet preference'),
                ('Non-Vegetarian', 'Eats all food'),
            ],
            'lifestyle': [
                ('Non-Smoker', 'Does not smoke'),
                ('Smoker', 'Smokes'),
                ('Non-Drinker', 'Does not drink alcohol'),
                ('Social Drinker', 'Drinks occasionally'),
            ],
            'values': [
                ('Eco-Conscious', 'Environmental awareness'),
                ('Animal Lover', 'Love for animals'),
                ('Adventure Seeker', 'Loves adventure'),
                ('Relaxation Focused', 'Prefers relaxation'),
                ('Cultural Explorer', 'Interested in cultures'),
            ],
        }

        created_tags = {}
        for category, tags_list in constraint_data.items():
            for name, description in tags_list:
                tag, created = ConstraintTag.objects.get_or_create(
                    category=category,
                    name=name,
                    defaults={'description': description}
                )
                created_tags[name] = tag
                if created:
                    self.stdout.write(f"✅ Created Constraint Tag: {name} ({category})")

        # Assign interests and tags to users
        users = UserProfile.objects.all()
        self.stdout.write(f"\n📝 Assigning interests to {users.count()} users...\n")

        for profile in users:
            # Skip users with no user account
            if not profile.user:
                continue

            # Randomly assign 3-5 interests
            num_interests = random.randint(3, 5)
            interest_list = random.sample(list(created_interests.values()), num_interests)
            profile.interests.set(interest_list)

            # Randomly assign 2-4 constraint tags
            num_tags = random.randint(2, 4)
            tag_list = random.sample(list(created_tags.values()), num_tags)
            profile.constraint_tags.set(tag_list)

            # Set travel preferences if not already set
            if not profile.travel_style:
                profile.travel_style = random.choice(['budget', 'luxury', 'adventure'])
            if not profile.pace:
                profile.pace = random.choice(['relaxed', 'moderate', 'fast_paced'])
            if not profile.accomodation_preference:
                profile.accomodation_preference = random.choice(['hostel', 'hotel', 'inn', 'camping'])

            # Set scores if default
            if profile.budget_level == 5:
                profile.budget_level = random.randint(1, 10)
            if profile.adventure_level == 5:
                profile.adventure_level = random.randint(1, 10)
            if profile.social_level == 5:
                profile.social_level = random.randint(1, 10)

            # Set DOB if not set (for age compatibility checks)
            if not profile.dob:
                from datetime import timedelta
                years_ago = random.randint(18, 60)
                profile.dob = timezone.now().date() - timedelta(days=365 * years_ago)

            profile.save()

            interests_str = ', '.join([i.name for i in profile.interests.all()])
            tags_str = ', '.join([t.name for t in profile.constraint_tags.all()])

            self.stdout.write(
                f"✅ {profile.user.username}\n"
                f"   Interests: {interests_str}\n"
                f"   Tags: {tags_str}\n"
                f"   Travel Style: {profile.travel_style}, Pace: {profile.pace}\n"
                f"   Scores: Budget={profile.budget_level}, Adventure={profile.adventure_level}, Social={profile.social_level}\n"
            )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Successfully populated {users.count()} users with interests and constraint tags!'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f'Now you can use cosine similarity matching to find travel buddies! 🚀'
            )
        )
