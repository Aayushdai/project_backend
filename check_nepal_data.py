import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_companion.settings')
import django
django.setup()

from django.contrib.auth.models import User
from apps.users.models import UserProfile
from apps.trips.models import Trip

nepal_users = User.objects.filter(username__startswith='nepal_').count()
nepal_profiles = UserProfile.objects.filter(user__username__startswith='nepal_').count()
nepal_trips = Trip.objects.filter(creator__user__username__startswith='nepal_').count()

print(f"Nepal Users Created: {nepal_users}")
print(f"Nepal Profiles Created: {nepal_profiles}")
print(f"Nepal Trips Created: {nepal_trips}")
print(f"TOTAL: {nepal_users + nepal_profiles + nepal_trips} objects in database")
