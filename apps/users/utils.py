import numpy as np
from datetime import datetime
from django.utils import timezone
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity
from apps.users.models import UserProfile, Interest, ConstraintTag


def get_user_age(dob):
    """Calculate user age from date of birth"""
    if not dob:
        return None
    today = timezone.now().date()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))


def check_constraint_compatibility(user1, user2):
    """
    ✅ SOFT CONSTRAINT MATCHING: Check if two users have compatible constraint tags.
    Now uses soft scoring via cosine similarity, but can still reject extreme mismatches.
    
    Since constraint tags are now part of the feature vector for cosine similarity,
    we make this check more permissive - allow matches unless there's a clear conflict.
    """
    # Get constraint tags for both users
    user1_tags = set(user1.constraint_tags.values_list('name', flat=True))
    user2_tags = set(user2.constraint_tags.values_list('name', flat=True))
    
    # If either has no constraints specified, they're open to anyone
    if not user1_tags or not user2_tags:
        return True
    
    # Check for diet conflicts (can't have vegetarian + non-vegetarian with same person)
    diet_tags_1 = {'Vegetarian', 'Vegan', 'Non-vegetarian', 'Halal', 'Kosher', 'Pescatarian'}
    diet_tags_user1 = user1_tags & diet_tags_1
    diet_tags_user2 = user2_tags & diet_tags_1
    
    # Check if diets are fundamentally incompatible
    if diet_tags_user1 and diet_tags_user2:
        # Vegetarian/Vegan is incompatible with Non-vegetarian
        veg_only_1 = diet_tags_user1 <= {'Vegetarian', 'Vegan'}
        veg_only_2 = diet_tags_user2 <= {'Vegetarian', 'Vegan'}
        non_veg_1 = 'Non-vegetarian' in diet_tags_user1
        non_veg_2 = 'Non-vegetarian' in diet_tags_user2
        
        # If one is strict veg and other is non-veg, reject
        if (veg_only_1 and non_veg_2) or (veg_only_2 and non_veg_1):
            return False
    
    # Check for smoking conflicts (smoker vs non-smoker)
    smoker_1 = 'Smoker' in user1_tags
    smoker_2 = 'Smoker' in user2_tags
    non_smoker_1 = 'Non-smoker' in user1_tags
    non_smoker_2 = 'Non-smoker' in user2_tags
    
    # If there's an explicit conflict, reject
    if (non_smoker_1 and smoker_2) or (non_smoker_2 and smoker_1):
        return False
    
    # Otherwise allow the match (similarity score will handle compatibility)
    return True


def check_age_compatibility(user1, user2):
    """
    ✅ AGE CONSTRAINT: Check if users fall within each other's preferred age ranges.
    Prevents teenager-elder mismatches.
    """
    age1 = get_user_age(user1.dob)
    age2 = get_user_age(user2.dob)
    
    # If either has no DOB, skip age check
    if age1 is None or age2 is None:
        return True
    
    # Check if user2's age is within user1's range
    user1_accepts_user2 = user1.min_match_age <= age2 <= user1.max_match_age
    # Check if user1's age is within user2's range
    user2_accepts_user1 = user2.min_match_age <= age1 <= user2.max_match_age
    
    return user1_accepts_user2 and user2_accepts_user1


def user_profile_to_vector(profile):
    """
    Convert user profile to a feature vector for cosine similarity.
    Includes: travel style, pace, accommodation, scores, destinations, interests, and constraint tags.
    
    ✅ WEIGHTED FEATURES:
    - Constraint tags (absolute tags) = 2x weight (higher priority for lifestyle compatibility)
    - Interests (soft matching) = 1x weight
    - Travel preferences & scores = 1x weight
    """
    # Categorical -> One-hot
    travel_style_map = {'budget': 0, 'luxury': 1, 'adventure': 2}
    pace_map = {'relaxed': 0, 'moderate': 1, 'fast_paced': 2}
    accom_map = {'hostel': 0, 'hotel': 1, 'inn': 2, 'camping': 3}

    cats = [
        travel_style_map.get(profile.travel_style, 1),
        pace_map.get(profile.pace, 1),
        accom_map.get(profile.accomodation_preference, 1),
    ]

    # Numerical scores (0-10 range)
    nums = [
        profile.budget_level,
        profile.adventure_level,
        profile.social_level,
    ]

    # Destination keywords
    dest_vector = [0] * 5
    dest_keywords = ['mountain', 'city', 'temples', 'nature', 'lake']
    for dest in profile.preferred_destinations.lower().replace(' ', ' ').split(','):
        for i, kw in enumerate(dest_keywords):
            if kw in dest:
                dest_vector[i] = 1

    # Interests vector (binary encoding) - 1x weight
    all_interests = Interest.objects.all().order_by('id')
    user_interests = set(profile.interests.values_list('id', flat=True))
    interests_vector = [1 if interest.id in user_interests else 0 for interest in all_interests]

    # ✅ Constraint Tags vector (binary encoding) - 2x weight (absolute tags get higher priority)
    all_tags = ConstraintTag.objects.all().order_by('id')
    user_tags = set(profile.constraint_tags.values_list('id', flat=True))
    tags_vector = [1 if tag.id in user_tags else 0 for tag in all_tags]
    
    # ✅ WEIGHT BOOST: Duplicate constraint tags to give them 2x weight in cosine similarity
    weighted_tags_vector = tags_vector + tags_vector

    # Combining everything: cats + nums + dest + interests + weighted_tags
    vector = np.array(cats + nums + dest_vector + interests_vector + weighted_tags_vector, dtype=float)

    # Scaling numerical features (0-1)
    scaler = MinMaxScaler(feature_range=(0, 1))
    vector[3:6] = scaler.fit_transform(vector[3:6].reshape(-1, 1)).flatten()

    return vector


# Find similar users matching using cosine similarity WITH strict constraints
def find_similar_users(current_profile, limit=9, min_similarity=0.65):
    """
    Find users similar to the current profile using cosine similarity.
    
    ✅ HARD FILTERS (strict filters - must pass):
    1. Age compatibility (within preferred ranges)
    2. Critical constraint tag conflicts (vegetarian-only vs non-veg, non-smoker vs smoker)
    
    ✅ SOFT MATCHING (cosine similarity score):
    - Travel style, pace, accommodation
    - Budget/adventure/social scores
    - Destinations and interests
    - ✨ Constraint tags (diet, lifestyle, values) - NEWLY ADDED!
    
    Higher similarity scores when users share:
    - Same interests and constraint tags
    - Similar travel preferences and scores
    - Matching lifestyle preferences
    
    Args:
        current_profile: UserProfile instance
        limit: Number of matches to return
        min_similarity: Minimum cosine similarity score (0.0-1.0)
    """
    current_vector = user_profile_to_vector(current_profile)
    similar = []
    current_age = get_user_age(current_profile.dob)

    for other in UserProfile.objects.exclude(user=current_profile.user).select_related('user').prefetch_related('interests', 'constraint_tags'):
        
        # ✅ HARD CONSTRAINT 1: Age compatibility
        if not check_age_compatibility(current_profile, other):
            print(f"⛔ {other.user.username}: Age incompatible")
            continue
        
        # ✅ HARD CONSTRAINT 2: Critical constraint tag compatibility (diet/smoking only)
        if not check_constraint_compatibility(current_profile, other):
            print(f"⛔ {other.user.username}: Critical constraint conflict (diet/smoking mismatch)")
            continue
        
        # ✅ SOFT MATCHING: Cosine similarity (now includes constraint tags!)
        other_vector = user_profile_to_vector(other)
        sim = cosine_similarity(
            current_vector.reshape(1, -1),
            other_vector.reshape(1, -1)
        )[0][0]

        if sim >= min_similarity:
            similar.append((other, round(sim, 3)))
            print(f"✅ {other.user.username}: Score {sim:.3f}")

    # Sorting by similarity descending
    similar.sort(key=lambda x: x[1], reverse=True)

    return similar[:limit]


def calculate_user_similarity(user1_profile, user2_profile):
    """
    Calculate similarity score between two users (0-100%).
    Returns a percentage score for display.
    """
    # Check hard constraints
    if not check_age_compatibility(user1_profile, user2_profile):
        return 0  # Incompatible age
    
    if not check_constraint_compatibility(user1_profile, user2_profile):
        return 0  # Incompatible constraints
    
    # Calculate cosine similarity
    user1_vector = user_profile_to_vector(user1_profile)
    user2_vector = user_profile_to_vector(user2_profile)
    
    sim = cosine_similarity(
        user1_vector.reshape(1, -1),
        user2_vector.reshape(1, -1)
    )[0][0]
    
    # Convert to 0-100% scale
    return round(sim * 100, 1)



  
