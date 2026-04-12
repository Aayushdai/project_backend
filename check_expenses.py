import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_companion.settings')
django.setup()

from apps.trips.models import Trip, TripExpenseBudget

print("=" * 60)
print("TRIP EXPENSES CHECK")
print("=" * 60)

# Get all trips
trips = Trip.objects.all()
print(f"\nTotal trips: {trips.count()}\n")

for trip in trips:
    print(f"Trip: {trip.title} (ID: {trip.id})")
    print(f"  Creator: {trip.creator}")
    print(f"  Created: {trip.created_at}")
    
    # Get expenses for this trip
    expenses = TripExpenseBudget.objects.filter(trip=trip)
    print(f"  Expenses count: {expenses.count()}")
    
    if expenses.exists():
        for expense in expenses:
            print(f"    - {expense.category}: Rs {expense.amount}")
    else:
        print("    (No expenses)")
    
    print(f"  Total Expense (calculated): Rs {trip.total_expense}")
    print()
