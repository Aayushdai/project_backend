from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.trips.models import Trip, City, TripExpenseBudget, TripReview
from apps.users.models import UserProfile
import random

class Command(BaseCommand):
    help = "Create fake completed trips with expenses and reviews for testing trip history"

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-id',
            type=int,
            help='User ID to create trips for',
        )
        parser.add_argument(
            '--count',
            type=int,
            default=5,
            help='Number of trips to create (default: 5)',
        )

    def handle(self, *args, **options):
        user_id = options.get('user_id')
        trip_count = options.get('count', 5)

        # Get the user or use the first available user
        if user_id:
            try:
                creator = UserProfile.objects.get(id=user_id)
            except UserProfile.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"User with ID {user_id} not found"))
                return
        else:
            creator = UserProfile.objects.first()
            if not creator:
                self.stdout.write(self.style.ERROR("No users found in database"))
                return
            self.stdout.write(f"Using user: {creator.user.username}")

        # Get or create test cities
        cities = list(City.objects.all())
        if not cities:
            self.stdout.write(self.style.WARNING("No cities found in database. Creating sample cities..."))
            cities = [
                City.objects.create(name="Kathmandu", country="Nepal"),
                City.objects.create(name="Pokhara", country="Nepal"),
                City.objects.create(name="Chitwan", country="Nepal"),
                City.objects.create(name="Delhi", country="India"),
                City.objects.create(name="Goa", country="India"),
            ]

        # Trip templates
        trip_templates = [
            {
                "title": "Himalayan Trek Adventures",
                "description": "An amazing trek through the Himalayan mountains with breathtaking views and local cuisine.",
                "days": 10,
                "expenses": [
                    ("Accommodation", 5000),
                    ("Food", 3000),
                    ("Transport", 2500),
                    ("Activities", 2000),
                ]
            },
            {
                "title": "Beach Getaway Paradise",
                "description": "Relax on pristine beaches, enjoy water sports, and experience the local culture.",
                "days": 7,
                "expenses": [
                    ("Hotel", 7000),
                    ("Meals", 2500),
                    ("Transport", 1500),
                    ("Beach Activities", 1500),
                ]
            },
            {
                "title": "Cultural Heritage Tour",
                "description": "Explore ancient temples, museums, and historical sites with a guided tour.",
                "days": 5,
                "expenses": [
                    ("Guide", 2000),
                    ("Hotel", 4000),
                    ("Food", 1500),
                    ("Entry Fees", 500),
                ]
            },
            {
                "title": "Adventure Sports Extravaganza",
                "description": "Paragliding, rock climbing, and extreme sports in scenic locations.",
                "days": 8,
                "expenses": [
                    ("Paragliding", 5000),
                    ("Equipment Rental", 2000),
                    ("Accommodation", 4000),
                    ("Food", 2000),
                ]
            },
            {
                "title": "Wildlife Safari Experience",
                "description": "Encounter exotic wildlife in their natural habitat with professional guides.",
                "days": 6,
                "expenses": [
                    ("Safari Permit", 3000),
                    ("Lodge", 5000),
                    ("Jeep Hire", 2000),
                    ("Food", 1500),
                ]
            },
            {
                "title": "Mountain Biking Quest",
                "description": "Challenge yourself on mountain trails with experienced riders.",
                "days": 4,
                "expenses": [
                    ("Bike Rental", 1000),
                    ("Hotel", 2000),
                    ("Food", 1000),
                    ("Guide", 1000),
                ]
            },
            {
                "title": "Spiritual Retreat",
                "description": "Meditation, yoga, and spiritual teachings in a peaceful setting.",
                "days": 7,
                "expenses": [
                    ("Retreat Fee", 8000),
                    ("Meals", 2000),
                    ("Transport", 1000),
                ]
            },
            {
                "title": "Photography Tour",
                "description": "Capture stunning landscapes and wildlife with professional photographers.",
                "days": 5,
                "expenses": [
                    ("Guide", 2500),
                    ("Transport", 1500),
                    ("Accommodation", 3000),
                    ("Food", 1000),
                ]
            },
        ]

        # Get other users for participants (excluding creator)
        other_users = list(UserProfile.objects.exclude(id=creator.id)[:20])

        created_count = 0
        for i in range(trip_count):
            template = trip_templates[i % len(trip_templates)]
            city = random.choice(cities)

            # Create trip with past date
            days_ago = random.randint(30, 365)
            end_date = timezone.now().date() - timedelta(days=days_ago)
            start_date = end_date - timedelta(days=template["days"])

            trip = Trip.objects.create(
                title=f"{template['title']} #{i+1}",
                destination=city,
                start_date=start_date,
                end_date=end_date,
                description=template["description"],
                creator=creator,
                is_public=random.choice([True, False]),
                trip_tags=[
                    ["Adventure", "Outdoor"],
                    ["Budget", "Moderate"],
                    ["Active", "Relaxed"],
                    ["Group", "Solo"],
                ][(i + random.randint(0, 3)) % 4]
            )

            # Add random participants
            if other_users:
                num_participants = random.randint(1, min(4, len(other_users)))
                participants = random.sample(other_users, num_participants)
                trip.participants.set(participants)

            # Add expenses
            for category, amount in template["expenses"]:
                TripExpenseBudget.objects.create(
                    trip=trip,
                    category=category,
                    amount=amount
                )

            # Add reviews from some participants
            if trip.participants.exists():
                for participant in random.sample(list(trip.participants.all()), 
                                                 random.randint(1, min(2, trip.participants.count()))):
                    TripReview.objects.get_or_create(
                        trip=trip,
                        reviewer=participant,
                        defaults={
                            "rating": random.randint(3, 5),
                            "text": random.choice([
                                "Amazing trip! Everyone was so friendly and the itinerary was perfect.",
                                "Had a great time exploring the destination. Would definitely travel again!",
                                "The organizer was very well-prepared. Everything went smoothly.",
                                "Met some wonderful people. This was the best trip ever!",
                                "Great value for money. Highly recommended for future travelers.",
                            ])
                        }
                    )

            created_count += 1
            self.stdout.write(
                self.style.SUCCESS(
                    f"✓ Created trip: {trip.title} ({start_date} to {end_date}) "
                    f"with {trip.participants.count()} participants and {trip.expense_budgets.count()} expenses"
                )
            )

        self.stdout.write(
            self.style.SUCCESS(f"\n✓ Successfully created {created_count} completed trips with expenses and reviews!")
        )
        self.stdout.write(self.style.WARNING(f"Creator: {creator.user.username}"))
