import os, django, random
from datetime import datetime, timedelta

os.environ['EMAIL_BACKEND'] = 'django.core.mail.backends.dummy.EmailBackend'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_companion.settings')
django.setup()

from django.contrib.auth.models import User
from apps.users.models import UserProfile
from apps.trips.models import Trip, City

print("Creating 100 users with 5 trips each...")

# Disable signal
from django.db.models.signals import post_save
from apps.users.signals import create_user_profile
post_save.disconnect(create_user_profile, sender=User)

# Get or create one city
city, _ = City.objects.get_or_create(name="Kathmandu", defaults={"country": "Nepal"})

# Create 100 users
print("Creating users...")
users = []
for i in range(100):
    u = User.objects.create_user(
        username=f"nepal_{i}",
        email=f"nepal_{i}@test.com",
        first_name=f"User",
        last_name=f"{i}",
    )
    users.append(u)
    if (i + 1) % 20 == 0:
        print(f"  ✓ {i + 1} users")

# Create profiles
print("Creating profiles...")
profiles = []
for user in users:
    p, _ = UserProfile.objects.get_or_create(
        user=user,
        defaults={'citizenship': 'Nepal', 'country': 'Nepal'}
    )
    profiles.append(p)

print(f"✓ {len(profiles)} profiles")

# Create trips
print("Creating trips...")
for idx, profile in enumerate(profiles):
    for j in range(5):
        start = datetime.now() + timedelta(days=random.randint(10, 60))
        Trip.objects.create(
            title=f"Trip {j+1}",
            description="Nepal trip",
            creator=profile,
            destination=city,
            start_date=start,
            end_date=start + timedelta(days=7),
            is_public=True,
        )
    
    if (idx + 1) % 20 == 0:
        print(f"  ✓ {(idx + 1) * 5} trips created")

# Reconnect signal
post_save.connect(create_user_profile, sender=User)

print("\n✅ Complete! 100 users, 500 trips")
