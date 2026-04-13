import os
import django
import random

# Disable email sending during population
os.environ['EMAIL_BACKEND'] = 'django.core.mail.backends.dummy.EmailBackend'

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_companion.settings')
django.setup()

from django.db import transaction
from apps.users.models import UserProfile
from apps.trips.models import Trip

print("=" * 60)
print("Adding Nepal Users to Trips (Min 5 per user)")
print("=" * 60)

# Get all Nepal users (those created with email pattern nepal*)
nepal_users = UserProfile.objects.filter(
    user__email__startswith='nepal_'
).all()

print(f"\n✓ Found {nepal_users.count()} Nepal users")

# Get all trips
all_trips = Trip.objects.all()
print(f"✓ Found {all_trips.count()} total trips")

# Add users to trips
print("\n👥 Adding users to trips (minimum 5 trips each)...")

users_with_joins = 0
total_joins = 0

with transaction.atomic():
    for idx, user_profile in enumerate(nepal_users):
        # Get trips created by other users (not this user's own trips)
        available_trips = all_trips.exclude(creator=user_profile)
        
        if available_trips.count() < 5:
            print(f"⚠️  User {idx + 1}: Only {available_trips.count()} trips available to join (need 5)")
            continue
        
        # Randomly select 5 trips to join
        trips_to_join = random.sample(list(available_trips), 5)
        
        # Add user to those trips
        for trip in trips_to_join:
            trip.participants.add(user_profile)
        
        users_with_joins += 1
        total_joins += 5
        
        if (idx + 1) % 20 == 0:
            print(f"  ✓ Processed {idx + 1} users ({total_joins} total joins)")

print(f"\n✓ Successfully added {users_with_joins} users to trips")
print(f"✓ Total trip joins: {total_joins}")

# Verify results
print("\n📊 Verification:")
users_in_trips = 0
sample_count = 0
for user in nepal_users:
    joined_trips_count = user.joined_trips.count()
    if joined_trips_count >= 5:
        users_in_trips += 1
    # Show a sample of 5 users
    if sample_count < 5:
        print(f"  • {user.user.first_name} {user.user.last_name}: {joined_trips_count} trips")
        sample_count += 1

print(f"\n✓ Users with 5+ trip memberships: {users_in_trips}/{nepal_users.count()}")

print("\n" + "=" * 60)
print("✅ Task completed!")
print("=" * 60)
