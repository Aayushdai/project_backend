import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_companion.settings')
django.setup()

from apps.trips.models import Trip, TripExpenseBudget

# Get the most recently created trip
trip = Trip.objects.order_by('-created_at').first()

if trip:
    print(f"Latest trip: {trip.title} (ID: {trip.id})")
    print(f"Created at: {trip.created_at}")
    
    expenses = TripExpenseBudget.objects.filter(trip=trip)
    print(f"Expenses count: {expenses.count()}")
    
    if expenses.exists():
        for exp in expenses:
            print(f"  - {exp.category}: Rs {exp.amount}")
    else:
        print("  (No expenses found)")
else:
    print("No trips found")
