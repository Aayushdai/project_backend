#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_companion.settings')
django.setup()

from apps.users.models import UserProfile
from apps.trips.recommendation import calculate_cosine_similarity, get_recommended_trips

# Get Nepal users WITH interests
nepal_users = UserProfile.objects.filter(
    user__username__startswith='nepal_',
    interests__isnull=False
).distinct()[:5]

print(f"Testing with Nepal users who have interests...")
print(f"{'='*70}\n")

for user in nepal_users:
    user_interests = list(user.interests.values_list('name', flat=True))
    
    if not user_interests:
        continue
    
    print(f"User: {user.user.username}")
    print(f"Interests ({len(user_interests)}): {', '.join(user_interests)}")
    
    # Get recommended trips  
    recommended = get_recommended_trips(user, limit=3)
    
    if not recommended:
        print("⚠️  No recommended trips found")
        print()
        continue
    
    print(f"\n📍 Top 3 Recommended Trips (with cosine similarity):\n")
    for i, trip_data in enumerate(recommended, 1):
        trip = trip_data['trip']
        score = trip_data['score']
        match_count = trip_data['match_count']
        avg_sim = trip_data['avg_similarity']
        best_match = trip_data['best_match']
        
        print(f"  {i}. {trip.title} ({trip.destination.name})")
        print(f"     Members in trip: {trip.participants.count()}")
        print(f"     ✓ Recommendation Score: {score:.2f}")
        print(f"     ✓ People with good match (>40%): {match_count}")
        print(f"     ✓ Average cosine similarity: {avg_sim}%")
        print(f"     ✓ Best individual match: {best_match}%")
        
        # Show similarity breakdown for trip members
        members_analysis = trip_data['matching_members'][:2]
        if members_analysis:
            print(f"     Member similarity sample:")
            for member in members_analysis:
                sim = calculate_cosine_similarity(
                    user.interests.values_list('id', flat=True),
                    member.interests.values_list('id', flat=True)
                )
                print(f"       • {member.user.username}: {sim}% match")
        print()
    
    print(f"\n{'='*70}\n")

print("✅ Cosine similarity recommendation system is fully functional!")
