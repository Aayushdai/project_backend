from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date
from apps.trips.models import Trip


class Command(BaseCommand):
    help = 'Marks all trips with end_date in the past as completed'

    def handle(self, *args, **options):
        today = date.today()
        
        # Find all trips that have ended but are not marked as completed
        past_trips = Trip.objects.filter(
            end_date__lt=today,
            is_completed=False
        )
        
        count = past_trips.count()
        if count > 0:
            past_trips.update(is_completed=True)
            self.stdout.write(
                self.style.SUCCESS(f'Successfully marked {count} trip(s) as completed')
            )
        else:
            self.stdout.write(self.style.WARNING('No incomplete trips found with past end dates'))
