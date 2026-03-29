import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_companion.settings')
django.setup()

from apps.users.models import Interest, ConstraintTag, UserProfile, Match, UserLoginHistory
from django.contrib.auth.models import User
from django.utils.timezone import now
from datetime import timedelta
import random

# Quick check what's in the database
print(f"Current Interests: {Interest.objects.count()}")
print(f"Current Constraint Tags: {ConstraintTag.objects.count()}")
print(f"Current Users: {User.objects.filter(username__in=['alex_traveler', 'priya_explorer', 'marco_beach']).count()}")
print(f"Current Profiles: {UserProfile.objects.count()}")
print(f"Current Matches: {Match.objects.count()}")
print(f"Current Login History: {UserLoginHistory.objects.count()}")
