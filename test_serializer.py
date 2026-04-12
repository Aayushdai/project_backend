import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_companion.settings')
django.setup()

from apps.trips.models import Trip
from apps.trips.serializers import TripSerializer

trip = Trip.objects.first()
if trip:
    print(f"Found trip: {trip.title}")
    serializer = TripSerializer(trip)
    data = serializer.data
    print(f"Has expense_budgets? {'expense_budgets' in data}")
    print(f"Expense budget count: {len(data.get('expense_budgets', []))}")
    print(f"Expense budgets: {data.get('expense_budgets')}")
else:
    print("No trips found")
