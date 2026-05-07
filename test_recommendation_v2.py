"""
Test script to validate new recommendation system
Shows debug output and trip rankings
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_companion.settings')
django.setup()

from django.contrib.auth.models import User
from apps.users.models import UserProfile
from apps.trips.models import Trip
from apps.trips.recommendation import (
    get_recommended_trips_v2,
    build_global_tag_list,
    build_tag_vector,
    calculate_member_compatibility,
    get_match_color_and_label
)
from datetime import date

print("=" * 80)
print("🧪 TESTING NEW RECOMMENDATION SYSTEM")
print("=" * 80)

# Get a test user (using one of the Hattiban users)
test_users = User.objects.filter(username__startswith='hattiban_luxury_user')
if test_users.exists():
    test_user = test_users.first()
    user_profile = test_user.userprofile
    
    print(f"\n👤 Test User: {test_user.username}")
    print(f"   Tags: {', '.join(user_profile.constraint_tags.values_list('name', flat=True))}")
    print(f"   Budget: {getattr(user_profile, 'budget_preference', 'N/A')}")
    print(f"   Pace: {getattr(user_profile, 'pace_preference', 'N/A')}")
    print(f"   Accommodation: {getattr(user_profile, 'accommodation_preference', 'N/A')}")
    
    # Show global tag list
    print(f"\n📊 Global Tag List:")
    global_tags = build_global_tag_list()
    print(f"   {', '.join(global_tags)}")
    
    # Show user's tag vector
    vector, tags = build_tag_vector(user_profile, global_tags)
    print(f"\n📈 User's Tag Vector:")
    tag_pairs = [(tags[i], vector[i]) for i in range(len(tags))]
    for tag, value in tag_pairs:
        print(f"   {tag}: {value}")
    
    # Get recommended trips with debug
    print(f"\n🔍 Fetching recommended trips for Hattiban destination...")
    recommended = get_recommended_trips_v2(
        user_profile, 
        destination='Hattiban',
        limit=20,
        debug=True
    )
    
    print("\n" + "=" * 80)
    print("📋 TRIP RANKINGS")
    print("=" * 80)
    
    if not recommended:
        print("❌ No trips found!")
    else:
        for idx, trip_result in enumerate(recommended, 1):
            trip = trip_result['trip']
            score = trip_result['score']
            color, label = get_match_color_and_label(score)
            
            print(f"\n{idx}. {trip.title}")
            print(f"   Destination: {trip.destination.name}")
            print(f"   Score: {score:.1f}/100")
            print(f"   Match: {label} ({color.upper()})")
            print(f"   Members: {trip.participants.count()}")
            print(f"   Individual scores: {trip_result['debug_info']['member_scores']}")
            print(f"   Average: {trip_result['avg_similarity']:.1f}/100")
    
    # Now test with ALL trips (not just Hattiban)
    print("\n" + "=" * 80)
    print("🌍 TESTING WITH ALL TRIPS")
    print("=" * 80)
    
    today = date.today()
    total_trips = Trip.objects.filter(
        is_public=True,
        end_date__gte=today,
        is_completed=False
    ).count()
    
    print(f"\nTotal public future trips: {total_trips}")
    
    all_recommended = get_recommended_trips_v2(
        user_profile,
        limit=50,
        debug=False
    )
    
    print(f"Top 10 recommendations:")
    print("-" * 80)
    
    for idx, trip_result in enumerate(all_recommended[:10], 1):
        trip = trip_result['trip']
        score = trip_result['score']
        color, label = get_match_color_and_label(score)
        
        print(f"{idx:2}. {trip.title:30} | {score:6.1f}/100 | {label:15} | {trip.destination.name}")
    
    # Score distribution
    print(f"\n📊 Score Distribution:")
    score_distribution = {
        'green': 0,
        'yellow': 0,
        'orange': 0,
        'red': 0
    }
    
    for trip_result in all_recommended:
        score = trip_result['score']
        color, _ = get_match_color_and_label(score)
        score_distribution[color] += 1
    
    print(f"   🟢 Green (70-100): {score_distribution['green']}")
    print(f"   🟡 Yellow (50-69): {score_distribution['yellow']}")
    print(f"   🟠 Orange (30-49): {score_distribution['orange']}")
    print(f"   🔴 Red (0-29): {score_distribution['red']}")
    
    print("\n" + "=" * 80)
    print("✅ TEST COMPLETE")
    print("=" * 80)

else:
    print("❌ No test users found. Please create test data first.")
