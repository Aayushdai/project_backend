"""
Cosine Similarity utilities for interest-based matching
Uses pure Python implementation without external ML libraries
"""
from django.db.models import Q
import math


def calculate_cosine_similarity(user_interests, other_interests):
    """
    Calculate true cosine similarity between two sets of interests.
    
    Treats each interest profile as a vector where each dimension is an interest.
    Cosine similarity = (A · B) / (||A|| × ||B||)
    
    Args:
        user_interests: List of interest IDs or interest objects for the current user
        other_interests: List of interest IDs or interest objects to compare
    
    Returns:
        Float between 0 and 100 representing similarity percentage
    """
    # Extract IDs if objects are passed
    user_ids = set()
    other_ids = set()
    
    for interest in user_interests:
        if isinstance(interest, int):
            user_ids.add(interest)
        else:
            user_ids.add(interest.id)
    
    for interest in other_interests:
        if isinstance(interest, int):
            other_ids.add(interest)
        else:
            other_ids.add(interest.id)
    
    # Handle edge cases
    if not user_ids or not other_ids:
        return 0.0
    
    # Calculate dot product (count of common interests)
    dot_product = len(user_ids & other_ids)
    
    # Calculate magnitudes (square root of number of interests)
    magnitude_user = math.sqrt(len(user_ids))
    magnitude_other = math.sqrt(len(other_ids))
    
    # Avoid division by zero
    if magnitude_user == 0 or magnitude_other == 0:
        return 0.0
    
    # Cosine similarity formula
    cosine_sim = dot_product / (magnitude_user * magnitude_other)
    
    # Convert to percentage (0-100)
    return round(cosine_sim * 100, 1)


def get_trip_member_matches(trip, user_profile):
    """
    Get matching members in a trip based on interest similarity.
    
    Args:
        trip: Trip object
        user_profile: UserProfile of the current user
    
    Returns:
        Dict with:
        - matching_members: List of matching user profiles
        - match_count: Number of members with good matches
        - avg_similarity: Average similarity score
        - best_match: Highest individual similarity
    """
    user_interests = list(user_profile.interests.values_list('id', flat=True))
    
    if not user_interests:
        return {
            'matching_members': [],
            'match_count': 0,
            'avg_similarity': 0.0,
            'best_match': 0.0,
            'members_by_similarity': []
        }
    
    members = trip.participants.all()
    matching_members = []
    similarities = []
    
    for member in members:
        if member.id == user_profile.id:
            continue  # Skip self
        
        member_interests = list(member.interests.values_list('id', flat=True))
        similarity = calculate_cosine_similarity(user_interests, member_interests)
        
        if similarity > 0:
            matching_members.append({
                'member': member,
                'similarity': similarity
            })
            similarities.append(similarity)
    
    # Sort by similarity descending
    matching_members.sort(key=lambda x: x['similarity'], reverse=True)
    
    avg_similarity = sum(similarities) / len(similarities) if similarities else 0.0
    best_match = max(similarities) if similarities else 0.0
    
    # Count members with "good" match (>40%)
    match_count = sum(1 for m in matching_members if m['similarity'] >= 40)
    
    return {
        'matching_members': [m['member'] for m in matching_members],
        'match_count': match_count,
        'avg_similarity': round(avg_similarity, 1),
        'best_match': round(best_match, 1),
        'members_by_similarity': matching_members
    }


def get_recommended_trips(user_profile, trips_queryset=None, destination=None, limit=None):
    """
    Get trips ranked by interest matching quality and member count.
    
    Ranking algorithm:
    1. Filter by destination (if provided)
    2. For each trip, calculate:
       - Number of members with good interest match (>40% similarity)
       - Average similarity score of all members
    3. Rank by: (match_count * weight1) + (avg_similarity * weight2)
    
    Args:
        user_profile: UserProfile of the current user
        trips_queryset: QuerySet of trips to filter (default: all public trips)
        destination: City name or City object to filter by
        limit: Maximum number of trips to return
    
    Returns:
        List of trips sorted by recommendation score
    """
    from apps.trips.models import Trip, City
    from datetime import date
    
    if trips_queryset is None:
        # Default to public, future trips
        today = date.today()
        trips_queryset = Trip.objects.filter(
            is_public=True,
            end_date__gte=today,
            is_completed=False
        )
    
    if destination:
        if isinstance(destination, str):
            trips_queryset = trips_queryset.filter(destination__name__iexact=destination)
        elif isinstance(destination, City):
            trips_queryset = trips_queryset.filter(destination=destination)
    
    # Score each trip
    scored_trips = []
    
    for trip in trips_queryset:
        match_info = get_trip_member_matches(trip, user_profile)
        
        # Scoring: prioritize trips with more members having good matches
        # Also consider average similarity
        match_count = match_info['match_count']
        avg_similarity = match_info['avg_similarity']
        
        # Weighted score: 70% on member count, 30% on average similarity
        score = (match_count * 0.7) + (avg_similarity * 0.3)
        
        scored_trips.append({
            'trip': trip,
            'score': score,
            'match_count': match_count,
            'avg_similarity': avg_similarity,
            'best_match': match_info['best_match'],
            'matching_members': match_info['matching_members']
        })
    
    # Sort by score descending
    scored_trips.sort(key=lambda x: x['score'], reverse=True)
    
    if limit:
        scored_trips = scored_trips[:limit]
    
    return scored_trips
