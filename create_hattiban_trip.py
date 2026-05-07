"""
Create a Hattiban trip with 5 users all having the same preferences and tags.

Preferences:
- Style: Luxury
- Pace: Fast-Paced
- Accommodation: Inn

Vibe Scores:
- Budget → Luxury: 5/10
- Chill → Extreme: 5/10
- Solo → Group: 3/10

Travel Interest Tags: Hiking, Photography, Mountains, Nightlife
"""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_companion.settings')

import django
django.setup()

from apps.users.models import User as DjangoUser, UserProfile, ConstraintTag
from apps.trips.models import Trip, City
from datetime import date, timedelta
import random

# Get or create Hattiban city
hattiban_city, _ = City.objects.get_or_create(name='Hattiban')

print("=" * 60)
print("🏔️  CREATING HATTIBAN TRIP WITH 5 LUXURY TRAVELERS")
print("=" * 60)

# Get or verify ConstraintTag exists
if not ConstraintTag.objects.exists():
    print("❌ ERROR: No ConstraintTag objects found. Please populate constraints first.")
    exit(1)

# Define the shared tags for all 5 users
SHARED_TAG_KEYWORDS = ['Hiking', 'Photography', 'Mountains', 'Nightlife']

def get_tags_by_keywords(keywords):
    """Get constraint tags by keywords"""
    tags = []
    for keyword in keywords:
        matching_tags = ConstraintTag.objects.filter(name__icontains=keyword)
        tags.extend(list(matching_tags))
    # Remove duplicates
    return list(set(tags))

# Get the shared tags
shared_tags = get_tags_by_keywords(SHARED_TAG_KEYWORDS)
print(f"\n📍 Found {len(shared_tags)} matching tags:")
for tag in shared_tags:
    print(f"   - {tag.name}")

if not shared_tags:
    print("⚠️  No tags found matching the keywords. Using random tags instead.")
    shared_tags = list(ConstraintTag.objects.all()[:5])

# Create 5 users with the same tags and preferences
users = []
print(f"\n👥 Creating 5 users with shared preferences...")

for i in range(5):
    username = f"hattiban_luxury_user{i+1}"
    user, created = DjangoUser.objects.get_or_create(
        username=username,
        defaults={'email': f'{username}@test.com'}
    )
    
    if created:
        user.set_password('password123')
        user.save()
        print(f"  ✓ Created user: {username}")
    else:
        print(f"  ✓ Using existing user: {username}")
    
    # Get or create UserProfile
    profile, _ = UserProfile.objects.get_or_create(user=user)
    
    # Assign all shared tags
    profile.constraint_tags.set(shared_tags)
    
    # Set preferences
    profile.budget_preference = 'Luxury'  # Style: Luxury
    profile.pace_preference = 'Fast-Paced'  # Pace: Fast-Paced
    profile.accommodation_preference = 'Inn'  # Accommodation: Inn
    
    # Vibe scores (scale 0-10)
    profile.budget_to_luxury_score = 5  # Budget → Luxury: 5/10
    profile.chill_to_extreme_score = 5  # Chill → Extreme: 5/10
    profile.solo_to_group_score = 3  # Solo → Group: 3/10
    
    # KYC and sharing enabled
    profile.is_kyc_approved = True
    profile.share_trip_activity = True
    profile.save()
    
    users.append(user)
    print(f"     Tags: {', '.join([t.name for t in shared_tags[:3]])}...")
    print(f"     Preferences: Luxury, Fast-Paced, Inn")

# Create the Hattiban trip
print(f"\n🏕️  Creating Hattiban trip...")
trip = Trip.objects.create(
    title='Hattiban',
    description='Luxury fast-paced adventure in the mountains with hiking, photography, and nightlife',
    destination=hattiban_city,
    start_date=date.today() + timedelta(days=15),
    end_date=date.today() + timedelta(days=22),
    is_public=True,
    is_completed=False,
    creator=users[0].userprofile,  # First user is creator
)

# Add other users as participants
user_profiles = [u.userprofile for u in users]
trip.participants.set(user_profiles[1:])

print(f"\n✅ TRIP CREATED!")
print(f"   Title: {trip.title}")
print(f"   Destination: {trip.destination.name}")
print(f"   Dates: {trip.start_date} → {trip.end_date}")
print(f"   Creator: {users[0].username}")
print(f"   Participants: {', '.join([u.username for u in users[1:]])}")
print(f"\n💡 All 5 users have matching preferences:")
print(f"   - Style: Luxury")
print(f"   - Pace: Fast-Paced")
print(f"   - Accommodation: Inn")
print(f"   - Tags: {', '.join([t.name for t in shared_tags])}")
print(f"   - Cosine Similarity: Should be HIGH (100% matching tags)!")
print("\n" + "=" * 60)
