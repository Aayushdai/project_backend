"""
Script to add the current user as a participant to some other trips
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.trips.models import Trip, TripReview
from apps.users.models import UserProfile
import random

class Command(BaseCommand):
    help = "Add user as participant to random completed trips"

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-id',
            type=int,
            help='User ID to add as participant',
        )
        parser.add_argument(
            '--count',
            type=int,
            default=3,
            help='Number of trips to join (default: 3)',
        )

    def handle(self, *args, **options):
        user_id = options.get('user_id', 1)
        num_trips = options.get('count', 3)

        try:
            user = UserProfile.objects.get(id=user_id)
        except UserProfile.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"User with ID {user_id} not found"))
            return

        # Get completed trips where user is not already a participant
        today = timezone.now().date()
        available_trips = Trip.objects.filter(
            end_date__lt=today
        ).exclude(
            participants=user
        ).exclude(
            creator=user
        )[:num_trips]

        if not available_trips:
            self.stdout.write(self.style.WARNING("No available trips to join"))
            return

        count = 0
        for trip in available_trips:
            trip.participants.add(user)
            
            # Optionally add a review
            if random.choice([True, False]):
                TripReview.objects.get_or_create(
                    trip=trip,
                    reviewer=user,
                    defaults={
                        "rating": random.randint(3, 5),
                        "text": random.choice([
                            "Amazing trip! Everyone was so friendly and the itinerary was perfect.",
                            "Had a great time exploring the destination. Would definitely travel again!",
                            "The organizer was very well-prepared. Everything went smoothly.",
                            "Met some wonderful people. This was the best trip ever!",
                            "Great value for money. Highly recommended for future travelers.",
                            "Wonderful experience with great people and amazing sights!",
                            "One of the best adventures I've had. Will definitely join again!",
                        ])
                    }
                )
                self.stdout.write(self.style.SUCCESS(f"✓ Added {user.user.username} to {trip.title} with review"))
            else:
                self.stdout.write(self.style.SUCCESS(f"✓ Added {user.user.username} to {trip.title}"))
            
            count += 1

        self.stdout.write(
            self.style.SUCCESS(f"\n✓ Successfully added user to {count} completed trips!")
        )
