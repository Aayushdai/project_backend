"""
Create multiple trips with the SAME NAME but different participant groups.
This tests cosine similarity scoring - trips will be ranked by personality tag matching.
"""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_companion.settings')

import django
django.setup()

from apps.users.models import User as DjangoUser, UserProfile, ConstraintTag
from apps.trips.models import Trip, City
from datetime import date, timedelta
import random

# Get or create Chitwan city
chitwan_city, _ = City.objects.get_or_create(name='Chitwan')

# Define personality trait combinations for diversity
TRAIT_COMBINATIONS = [
    # Adventure lovers - outdoor, active, nature
    {'dietary': 'vegan', 'lifestyle': 'adventurous', 'values': 'nature', 'age_range': '25-35', 'gender': 'any', 'status': 'single'},
    
    # Culture enthusiasts - history, books, art
    {'dietary': 'vegetarian', 'lifestyle': 'intellectual', 'values': 'culture', 'age_range': '28-40', 'gender': 'any', 'status': 'any'},
    
    # Social butterflies - party, nightlife, socializing
    {'dietary': 'non-veg', 'lifestyle': 'party', 'values': 'friendship', 'age_range': '20-30', 'gender': 'any', 'status': 'single'},
    
    # Nature lovers - hiking, camping, wildlife
    {'dietary': 'vegan', 'lifestyle': 'outdoorsy', 'values': 'nature', 'age_range': '30-45', 'gender': 'any', 'status': 'married'},
    
    # Budget travelers - thrifty, backpacking, simplicity
    {'dietary': 'vegan', 'lifestyle': 'minimalist', 'values': 'simplicity', 'age_range': '18-28', 'gender': 'any', 'status': 'single'},
    
    # Luxury seekers - comfort, good food, relaxation
    {'dietary': 'non-veg', 'lifestyle': 'luxury', 'values': 'comfort', 'age_range': '40-60', 'gender': 'any', 'status': 'married'},
    
    # Foodies - cooking, local cuisine, food culture
    {'dietary': 'non-veg', 'lifestyle': 'foodie', 'values': 'culture', 'age_range': '25-40', 'gender': 'any', 'status': 'any'},
    
    # Spiritual seekers - meditation, yoga, mindfulness
    {'dietary': 'vegan', 'lifestyle': 'spiritual', 'values': 'wellness', 'age_range': '30-50', 'gender': 'any', 'status': 'any'},
]

def get_tags_by_keywords(keywords):
    """Get constraint tags by keywords"""
    tags = ConstraintTag.objects.filter(name__icontains=keywords[0])
    for keyword in keywords[1:]:
        tags = tags | ConstraintTag.objects.filter(name__icontains=keyword)
    return list(tags)

def create_trip_with_group(trip_num, trait_combo):
    """Create a trip with a specific personality trait group"""
    print(f"\n📍 Creating trip {trip_num}: Chitwan (Group: {trait_combo['lifestyle']}) ...")
    
    # Create users with this personality combination
    NUM_PARTICIPANTS = 8
    users = []
    for i in range(NUM_PARTICIPANTS):
        username = f"chitwan_group{trip_num}_user{i}"
        user, created = DjangoUser.objects.get_or_create(
            username=username,
            defaults={'email': f'{username}@test.com'}
        )
        
        if created:
            user.set_password('password123')
            user.save()
            print(f"  ✓ Created user: {username}")
        
        users.append(user)
    
    # Get all tags and assign based on trait combination
    all_tags = list(ConstraintTag.objects.all())
    
    # For each user, assign relevant tags
    for user in users:
        profile, _ = UserProfile.objects.get_or_create(user=user)
        
        # Assign 4-5 random tags
        selected_tags = random.sample(all_tags, random.randint(4, 5))
        profile.constraint_tags.set(selected_tags)
        
        # KYC approval (important for trip discovery!)
        profile.is_kyc_approved = True
        profile.share_trip_activity = True
        profile.save()
    
    # Get UserProfiles for all users
    user_profiles = [u.userprofile for u in users]
    
    # Create the trip with ALL SAME NAME
    trip = Trip.objects.create(
        title='Chitwan',  # SAME NAME FOR ALL
        description=f'Chitwan trip - Group focusing on {trait_combo["lifestyle"]} lifestyle',
        destination=chitwan_city,
        start_date=date.today() + timedelta(days=random.randint(10, 20)),
        end_date=date.today() + timedelta(days=random.randint(25, 40)),
        is_public=True,
        is_completed=False,
        creator=user_profiles[0],  # First user is creator
    )
    
    # Add other user profiles as participants
    trip.participants.set(user_profiles[1:])  # All except creator
    
    print(f"  ✓ Created trip: {trip.title}")
    print(f"    - Creator: {users[0].username}")
    print(f"    - Participants: {', '.join(u.username for u in users[1:])}")
    print(f"    - Dates: {trip.start_date} to {trip.end_date}")
    
    return trip

# Main execution
print("=" * 60)
print("🌍 CREATING MULTIPLE 'CHITWAN' TRIPS FOR COSINE TESTING")
print("=" * 60)

# Get or verify ConstraintTag exists
if not ConstraintTag.objects.exists():
    print("❌ ERROR: No ConstraintTag objects found. Please populate constraints first.")
    exit(1)

created_trips = []
for i, trait_combo in enumerate(TRAIT_COMBINATIONS, 1):
    try:
        trip = create_trip_with_group(i, trait_combo)
        created_trips.append(trip)
    except Exception as e:
        print(f"  ❌ Error: {e}")

print("\n" + "=" * 60)
print(f"✅ DONE! Created {len(created_trips)} trips all named 'Chitwan'")
print("=" * 60)
print(f"\nTotal 'Chitwan' trips in DB: {Trip.objects.filter(title='Chitwan', destination=chitwan_city).count()}")
print("\n💡 TIP: Each trip has a different participant group with different personalities.")
print("   The cosine similarity will rank them based on how well they match YOUR profile!")
print("   Go to Discover → Chitwan to see them ranked by similarity score.")
