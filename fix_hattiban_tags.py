import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_companion.settings')
django.setup()

from django.contrib.auth.models import User
from apps.users.models import UserProfile
from apps.trips.models import Trip, ConstraintTag, City
from datetime import date, timedelta

print("=" * 60)
print("🔧 FIXING HATTIBAN TRIP WITH CORRECT TAGS")
print("=" * 60)

# Delete old Hattiban trip and users
print("\n🗑️  Cleaning up old Hattiban data...")
old_users = User.objects.filter(username__startswith='hattiban_luxury_user')
Trip.objects.filter(title='Hattiban').delete()
old_users.delete()
print("✓ Old data removed")

# Get or create Hattiban city
hattiban_city, _ = City.objects.get_or_create(
    name='Hattiban',
    defaults={'country': 'Nepal', 'latitude': 27.6939, 'longitude': 85.2920}
)
print(f"✓ City: {hattiban_city.name}")

# Get tags by exact names - YOUR EXACT TAGS
tag_names = ['Hiking', 'Photography', 'Mountains', 'Nightlife']
shared_tags = list(ConstraintTag.objects.filter(name__in=tag_names))

print(f"\n🏷️  Looking for tags: {tag_names}")

# Create missing tags
created_count = 0
for tag_name in tag_names:
    if not ConstraintTag.objects.filter(name=tag_name).exists():
        ConstraintTag.objects.create(name=tag_name)
        created_count += 1
        print(f"   ✓ Created missing tag: {tag_name}")

# Get all tags again
shared_tags = ConstraintTag.objects.filter(name__in=tag_names)
print(f"✓ Found {shared_tags.count()} matching tags:")
for tag in shared_tags:
    print(f"   - {tag.name}")

# Create 5 users with YOUR exact preferences and tags
print(f"\n👥 Creating 5 users with YOUR exact preferences...")
users = []
for i in range(1, 6):
    username = f'hattiban_luxury_user{i}'
    email = f'{username}@test.com'
    
    # Create or get user
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            'email': email,
            'first_name': f'Hattiban{i}',
            'last_name': 'Luxury',
            'is_active': True
        }
    )
    user.set_password('testpass123')
    user.save()
    
    # Create profile with YOUR exact preferences
    profile, _ = UserProfile.objects.get_or_create(
        user=user,
        defaults={
            'budget_preference': 'Luxury',
            'pace_preference': 'Fast-Paced',
            'accommodation_preference': 'Inn',
            'budget_to_luxury_score': 5,
            'chill_to_extreme_score': 5,
            'solo_to_group_score': 3,
            'is_kyc_approved': True,
            'share_trip_activity': True
        }
    )
    
    # Assign YOUR exact tags
    profile.constraint_tags.set(shared_tags)
    profile.save()
    
    users.append(user)
    print(f"  ✓ Created user: {username}")
    print(f"     Tags: {', '.join([t.name for t in shared_tags])}")
    print(f"     Preferences: Luxury, Fast-Paced, Inn")

# Create Hattiban trip
print(f"\n🏕️  Creating Hattiban trip...")
trip = Trip.objects.create(
    title='Hattiban',
    description='Perfect luxury trip for you!',
    destination=hattiban_city,
    start_date=date(2026, 5, 22),
    end_date=date(2026, 5, 29),
    creator=users[0].userprofile,
    is_public=True,
    is_completed=False
)

# Add other 4 users as participants
trip.participants.add(*[u.userprofile for u in users[1:]])
trip.save()

print("\n✅ PERFECT MATCH TRIP CREATED!")
print("=" * 60)
print(f"   Title: {trip.title}")
print(f"   Destination: {hattiban_city.name}")
print(f"   Dates: {trip.start_date} → {trip.end_date}")
print(f"   Creator: {users[0].username}")
print(f"   Participants: {', '.join([u.username for u in users[1:]])}")
print(f"\n💡 ALL 5 users have MATCHING tags:")
print(f"   {', '.join([t.name for t in shared_tags])}")
print(f"\n💡 ALL 5 users have YOUR preferences:")
print(f"   - Style: Luxury")
print(f"   - Pace: Fast-Paced")
print(f"   - Accommodation: Inn")
print(f"\n🎯 Cosine Similarity: Should be 100% MATCH! ✨")
print("=" * 60)
