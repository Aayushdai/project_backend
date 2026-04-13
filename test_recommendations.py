#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_companion.settings')
django.setup()

from apps.users.models import UserProfile
from apps.trips.recommendation import calculate_cosine_similarity, get_recommended_trips

# Get a test user
users = UserProfile.objects.all()[:3]

if not users:
    print("❌ No users found in database!")
    exit(1)

for user in users:
    print(f"\n{'='*60}")
    print(f"User: {user.user.username}")
    interests = list(user.interests.values_list('name', flat=True))
    print(f"Interests ({len(interests)}): {', '.join(interests[:8])}")
    
    # Get recommended trips
    recommended = get_recommended_trips(user, limit=5)
    
    if not recommended:
        print("⚠️  No recommended trips found")
        continue
    
    print(f"\n📍 Top 5 Recommended Trips:")
    for i, trip_data in enumerate(recommended, 1):
        trip = trip_data['trip']
        score = trip_data['score']
        match_count = trip_data['match_count']
        avg_sim = trip_data['avg_similarity']
        best_match = trip_data['best_match']
        
        print(f"\n  {i}. {trip.title}")
        print(f"     Destination: {trip.destination.name}")
        print(f"     Members: {trip.participants.count()}")
        print(f"     ✓ Score: {score:.2f}")
        print(f"     ✓ Match Count: {match_count} people (>40% similarity)")
        print(f"     ✓ Avg Similarity: {avg_sim}%")
        print(f"     ✓ Best Match: {best_match}%")

print(f"\n{'='*60}")
print("✅ Recommendation system is working!")
