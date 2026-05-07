"""
RECOMMENDATION SYSTEM V3 - Complete Rewrite
=========================================

FIXED ISSUES:
1. Separated HARD constraints from SOFT preferences
   - Hard constraints: age, gender, diet, smoking, alcohol, lifestyle
   - Soft preferences: interests (activities, destinations, experiences)

2. Now uses Interest model for soft preferences (not constraint_tags)

3. Proper cosine similarity on actual interests users have selected

4. Weighted hybrid scoring:
   - Interest similarity: 50% (cosine on user interests)
   - Vibe similarity: 20% (preferences/sliders)
   - Lifestyle compatibility: 30% (hard constraints)

5. Realistic thresholds:
   - 70-100: Green (Good Match)
   - 50-69: Yellow (Moderate Match)
   - 30-49: Orange (Weak Match)
   - 0-29: Red (Poor Match)
"""

import math
from django.db.models import Q
from datetime import date


# ============================================================================
# HARD CONSTRAINT KEYWORDS (for identification and grouping)
# ============================================================================

HARD_CONSTRAINT_CATEGORIES = {
    'age': ['18-25', '25-35', '35-50', '50+'],
    'gender': ['Men Only', 'Women Only', 'Mixed Group'],
    'diet': ['Vegetarian', 'Vegan', 'Non-vegetarian', 'Pescatarian', 
             'Dairy-free', 'Gluten-free', 'Halal', 'Kosher'],
    'alcohol': ['Drinks Alcohol', 'Non-drinker'],
    'smoking': ['Smoker', 'Non-smoker'],
    'lifestyle': ['Fitness Focused', 'Early Riser', 'Night Owl', 
                  'Party Person', 'Quiet & Homebody'],
    'relationship': ['Solo Traveler', 'Partnered', 'Single']
}


# ============================================================================
# TAG NORMALIZATION
# ============================================================================

def normalize_tag_name(tag_name):
    """
    Normalize tag name for consistent matching
    
    Args:
        tag_name: Raw tag name from database
        
    Returns:
        Normalized tag name (lowercase, stripped whitespace)
    """
    if not tag_name:
        return ""
    
    return tag_name.strip().lower()


def is_hard_constraint(tag_name):
    """
    Check if a tag is a hard constraint
    
    Args:
        tag_name: Tag name (will be normalized)
        
    Returns:
        True if this is a hard constraint, False if soft preference
    """
    normalized = normalize_tag_name(tag_name)
    
    for category, keywords in HARD_CONSTRAINT_CATEGORIES.items():
        if any(normalize_tag_name(kw) == normalized for kw in keywords):
            return True
    
    return False


# ============================================================================
# INTEREST VECTOR BUILDING (Using Interest Model)
# ============================================================================

def build_global_interest_list():
    """
    Build a consistent global list of all interests for binary vector encoding
    
    This uses the Interest model which contains ONLY soft preferences
    
    Returns:
        Sorted list of all interest names
    """
    from apps.users.models import Interest
    
    interests = Interest.objects.all().values_list('name', flat=True)
    all_interests = [normalize_tag_name(interest) for interest in interests]
    
    return sorted(list(set(all_interests)))


def build_interest_vector(user_profile, global_interest_list=None):
    """
    Build binary vector of user's interests (soft preferences only)
    
    Args:
        user_profile: UserProfile object
        global_interest_list: Pre-computed list of all interests (for consistency)
        
    Returns:
        Tuple: (vector as list of 0/1, interest_names_list)
    """
    if global_interest_list is None:
        global_interest_list = build_global_interest_list()
    
    # Get user's interests
    user_interests = user_profile.interests.values_list('name', flat=True)
    user_interests_normalized = set(normalize_tag_name(interest) for interest in user_interests)
    
    # Build binary vector
    vector = []
    for interest in global_interest_list:
        vector.append(1 if interest in user_interests_normalized else 0)
    
    return vector, global_interest_list


# ============================================================================
# COSINE SIMILARITY
# ============================================================================

def calculate_cosine_similarity(vector1, vector2):
    """
    Calculate cosine similarity between two binary vectors
    
    Formula: (A·B) / (||A|| × ||B||)
    
    Args:
        vector1: List of 0/1 values
        vector2: List of 0/1 values
        
    Returns:
        Float between 0 and 1 (0=no similarity, 1=perfect match)
    """
    if not vector1 or not vector2 or len(vector1) != len(vector2):
        return 0.0
    
    # Handle empty vectors (no interests)
    if sum(vector1) == 0 or sum(vector2) == 0:
        # Both have no interests - neutral match (0.5)
        if sum(vector1) == 0 and sum(vector2) == 0:
            return 0.5
        # One has interests, other doesn't - penalize slightly
        return 0.2
    
    # Dot product (number of shared interests)
    dot_product = sum(v1 * v2 for v1, v2 in zip(vector1, vector2))
    
    # Magnitudes
    mag1 = math.sqrt(sum(v ** 2 for v in vector1))
    mag2 = math.sqrt(sum(v ** 2 for v in vector2))
    
    # Cosine similarity
    if mag1 == 0 or mag2 == 0:
        return 0.0
    
    cosine_sim = dot_product / (mag1 * mag2)
    
    return round(cosine_sim, 4)


# ============================================================================
# HARD CONSTRAINT CHECKING
# ============================================================================

def check_hard_constraint_compatibility(user_profile, target_profile, debug=False):
    """
    Check if two users pass hard constraint compatibility gates
    
    Returns:
        Tuple: (is_compatible: bool, penalty: float 0-1)
        penalty 0 = fully compatible, 1 = fully incompatible
    """
    penalty = 0.0
    
    # Get hard constraints for both users
    user_constraints = set()
    target_constraints = set()
    
    # Extract hard constraints from constraint_tags
    user_tags = user_profile.constraint_tags.values_list('name', flat=True)
    for tag in user_tags:
        if is_hard_constraint(tag):
            user_constraints.add(normalize_tag_name(tag))
    
    target_tags = target_profile.constraint_tags.values_list('name', flat=True)
    for tag in target_tags:
        if is_hard_constraint(tag):
            target_constraints.add(normalize_tag_name(tag))
    
    if debug:
        print(f"  User hard constraints: {user_constraints}")
        print(f"  Target hard constraints: {target_constraints}")
    
    # Check for specific incompatibilities
    
    # 1. Age compatibility
    user_ages = {c for c in user_constraints if c in ['18-25', '25-35', '35-50', '50+']}
    target_ages = {c for c in target_constraints if c in ['18-25', '25-35', '35-50', '50+']}
    
    if user_ages and target_ages and user_ages != target_ages:
        penalty += 0.15  # Age mismatch penalty
    
    # 2. Gender preference compatibility
    user_gender = {c for c in user_constraints if c in ['men only', 'women only', 'mixed group']}
    target_gender = {c for c in target_constraints if c in ['men only', 'women only', 'mixed group']}
    
    if user_gender and target_gender:
        # If one specifies gender but other doesn't, small penalty
        # If both specify conflicting gender, higher penalty
        if user_gender != target_gender:
            penalty += 0.1
    
    # 3. Diet compatibility
    user_diet = {c for c in user_constraints if c in [
        'vegetarian', 'vegan', 'non-vegetarian', 'pescatarian',
        'dairy-free', 'gluten-free', 'halal', 'kosher'
    ]}
    target_diet = {c for c in target_constraints if c in [
        'vegetarian', 'vegan', 'non-vegetarian', 'pescatarian',
        'dairy-free', 'gluten-free', 'halal', 'kosher'
    ]}
    
    # Check if diets are compatible
    if user_diet and target_diet:
        # Vegetarian/Vegan incompatible with Non-vegetarian
        user_is_strict_veg = 'vegetarian' in user_diet or 'vegan' in user_diet
        target_is_strict_veg = 'vegetarian' in target_diet or 'vegan' in target_diet
        
        if user_is_strict_veg and 'non-vegetarian' in target_diet:
            penalty += 0.2  # Moderate penalty for diet conflict
        elif not user_is_strict_veg and ('vegan' in target_diet):
            penalty += 0.15  # Mild penalty for vegan vs non-veg
    
    # 4. Alcohol compatibility
    user_alcohol = {c for c in user_constraints if c in ['drinks alcohol', 'non-drinker']}
    target_alcohol = {c for c in target_constraints if c in ['drinks alcohol', 'non-drinker']}
    
    if user_alcohol and target_alcohol and user_alcohol != target_alcohol:
        penalty += 0.1  # Mild penalty for alcohol preference mismatch
    
    # 5. Smoking compatibility
    user_smoking = {c for c in user_constraints if c in ['smoker', 'non-smoker']}
    target_smoking = {c for c in target_constraints if c in ['smoker', 'non-smoker']}
    
    if user_smoking and target_smoking and user_smoking != target_smoking:
        penalty += 0.15  # Moderate penalty for smoking mismatch
    
    # Cap penalty at 0.3 (can reduce score by max 30%)
    penalty = min(0.3, penalty)
    
    is_compatible = penalty < 0.3
    
    if debug:
        print(f"  Hard constraint penalty: {penalty:.2f}")
        print(f"  Is compatible: {is_compatible}")
    
    return is_compatible, penalty


# ============================================================================
# VIBE SIMILARITY (Preferences & Sliders)
# ============================================================================

def calculate_vibe_similarity(user_profile, target_profile, debug=False):
    """
    Calculate similarity based on travel preferences and sliders
    
    Includes:
    - Travel style (budget, mid-range, luxury)
    - Pace (relaxed, moderate, fast-paced)
    - Accommodation preference
    - Vibe scores (budget_level, adventure_level, social_level)
    
    Returns:
        Float between 0 and 1
    """
    similarity_scores = []
    
    # Travel style preference
    if hasattr(user_profile, 'travel_style') and user_profile.travel_style:
        if hasattr(target_profile, 'travel_style') and target_profile.travel_style:
            if user_profile.travel_style == target_profile.travel_style:
                similarity_scores.append(1.0)
            else:
                similarity_scores.append(0.5)  # Different but okay
        else:
            similarity_scores.append(0.8)  # User has preference, target doesn't
    
    # Pace preference
    if hasattr(user_profile, 'pace') and user_profile.pace:
        if hasattr(target_profile, 'pace') and target_profile.pace:
            if user_profile.pace == target_profile.pace:
                similarity_scores.append(1.0)
            else:
                similarity_scores.append(0.6)  # Different paces can work
        else:
            similarity_scores.append(0.8)
    
    # Accommodation preference
    if hasattr(user_profile, 'accomodation_preference') and user_profile.accomodation_preference:
        if hasattr(target_profile, 'accomodation_preference') and target_profile.accomodation_preference:
            if user_profile.accomodation_preference == target_profile.accomodation_preference:
                similarity_scores.append(1.0)
            else:
                similarity_scores.append(0.5)
        else:
            similarity_scores.append(0.8)
    
    # Vibe sliders (budget, adventure, social)
    vibe_fields = ['budget_level', 'adventure_level', 'social_level']
    
    for field in vibe_fields:
        if hasattr(user_profile, field) and hasattr(target_profile, field):
            user_val = getattr(user_profile, field, None)
            target_val = getattr(target_profile, field, None)
            
            if user_val is not None and target_val is not None:
                # Calculate similarity: closer values = higher similarity
                # Scale 0-10, so max diff is 10
                diff = abs(user_val - target_val)
                field_similarity = max(0, 1.0 - (diff / 10.0))
                similarity_scores.append(field_similarity)
    
    if debug:
        print(f"  Vibe similarity scores: {similarity_scores}")
    
    # Return average vibe similarity, or 0.5 if no vibe data
    return sum(similarity_scores) / len(similarity_scores) if similarity_scores else 0.5


# ============================================================================
# MEMBER COMPATIBILITY CALCULATION
# ============================================================================

def calculate_member_compatibility(user_profile, member_profile, debug=False):
    """
    Calculate final compatibility score between two users
    
    Uses hybrid scoring:
    - 50% interest similarity (cosine on user interests)
    - 20% vibe similarity (travel preferences/sliders)
    - 30% lifestyle compatibility (hard constraints)
    
    Args:
        user_profile: Current user's profile
        member_profile: Trip member's profile
        debug: Enable debug output
        
    Returns:
        Tuple: (final_score 0-1, debug_info dict)
    """
    debug_info = {}
    
    # Build interest vectors
    global_interests = build_global_interest_list()
    user_vector, _ = build_interest_vector(user_profile, global_interests)
    member_vector, _ = build_interest_vector(member_profile, global_interests)
    
    # 1. Interest similarity (cosine)
    interest_sim = calculate_cosine_similarity(user_vector, member_vector)
    debug_info['interest_similarity'] = interest_sim
    
    # 2. Vibe similarity
    vibe_sim = calculate_vibe_similarity(user_profile, member_profile, debug=debug)
    debug_info['vibe_similarity'] = vibe_sim
    
    # 3. Hard constraint compatibility
    is_compatible, constraint_penalty = check_hard_constraint_compatibility(
        user_profile, member_profile, debug=debug
    )
    lifestyle_compat = max(0, 1.0 - constraint_penalty)
    debug_info['lifestyle_compatibility'] = lifestyle_compat
    debug_info['hard_constraint_penalty'] = constraint_penalty
    
    # Weighted hybrid score
    final_score = (
        interest_sim * 0.5 +       # 50% - interests
        vibe_sim * 0.2 +           # 20% - vibe/preferences
        lifestyle_compat * 0.3     # 30% - hard constraints
    )
    
    debug_info['final_score'] = round(final_score, 4)
    
    if debug:
        print(f"  Interest similarity: {interest_sim:.2%}")
        print(f"  Vibe similarity: {vibe_sim:.2%}")
        print(f"  Lifestyle compatibility: {lifestyle_compat:.2%}")
        print(f"  Final weighted score: {final_score:.2%}")
    
    return final_score, debug_info


# ============================================================================
# TRIP COMPATIBILITY CALCULATION
# ============================================================================

def calculate_trip_compatibility(trip, user_profile, debug=False):
    """
    Calculate how compatible a user is with a trip (based on trip members)
    
    Algorithm:
    1. Compare current user against EACH trip member individually
    2. Calculate per-member compatibility scores
    3. Average all member scores (exclude self-comparison)
    4. Return trip score (0-100 scale)
    
    Args:
        trip: Trip object
        user_profile: Current user's profile
        debug: Enable debug output
        
    Returns:
        Tuple: (trip_score 0-100, debug_info dict)
    """
    members = list(trip.participants.all())
    
    if debug:
        print(f"\n📊 Calculating trip compatibility: '{trip.title}'")
        print(f"   Trip has {len(members)} members")
    
    member_scores = []
    
    for member in members:
        # Skip self-comparison
        if member.id == user_profile.id:
            if debug:
                print(f"   - Skipping self ({member.user.username})")
            continue
        
        score, member_info = calculate_member_compatibility(
            user_profile, member, debug=debug
        )
        member_scores.append(score)
        
        if debug:
            print(f"   - Member {member.user.username}: {score:.1%} match")
    
    # Calculate average trip score
    if not member_scores:
        trip_score = 0.0
        avg_score = 0.0
    else:
        avg_score = sum(member_scores) / len(member_scores)
        trip_score = avg_score * 100  # Scale to 0-100
    
    debug_info = {
        'trip_id': trip.id,
        'trip_title': trip.title,
        'member_count': len(members),
        'member_scores': [round(s * 100, 1) for s in member_scores],
        'average_member_score': round(avg_score * 100, 1),
        'trip_score': round(trip_score, 1),
    }
    
    if debug:
        print(f"\n✅ Trip Score: {trip_score:.1f}/100 (avg: {avg_score:.1%})")
    
    return trip_score, debug_info


# ============================================================================
# RECOMMENDED TRIPS RANKING
# ============================================================================

def get_recommended_trips_v3(user_profile, trips_queryset=None, destination=None, limit=None, debug=False):
    """
    Get trips ranked by realistic compatibility scoring
    
    Args:
        user_profile: UserProfile of current user
        trips_queryset: Trips to evaluate (default: all public future trips)
        destination: Filter by destination name or object
        limit: Max trips to return
        debug: Enable debug logging
        
    Returns:
        List of dicts with trip and scores, sorted best-to-worst
    """
    from apps.trips.models import Trip
    
    if trips_queryset is None:
        today = date.today()
        trips_queryset = Trip.objects.filter(
            is_public=True,
            end_date__gte=today,
            is_completed=False
        )
    
    if destination:
        if isinstance(destination, str):
            trips_queryset = trips_queryset.filter(destination__name__iexact=destination)
        else:
            trips_queryset = trips_queryset.filter(destination=destination)
    
    scored_trips = []
    
    for trip in trips_queryset:
        trip_score, debug_info = calculate_trip_compatibility(
            trip, user_profile, debug=debug
        )
        
        scored_trips.append({
            'trip': trip,
            'score': trip_score,
            'avg_similarity': debug_info['average_member_score'],
            'match_count': len([s for s in debug_info['member_scores'] if s >= 70]),
            'best_match': max(debug_info['member_scores']) if debug_info['member_scores'] else 0,
            'debug_info': debug_info
        })
    
    # Sort by score descending
    scored_trips.sort(key=lambda x: x['score'], reverse=True)
    
    if limit:
        scored_trips = scored_trips[:limit]
    
    return scored_trips


# ============================================================================
# SCORE INTERPRETATION THRESHOLDS
# ============================================================================

def get_match_color_and_label(score):
    """
    Convert score (0-100) to UI color and label
    
    Thresholds:
    - 70-100: Good Match (Green)
    - 50-69: Moderate Match (Yellow)
    - 30-49: Weak Match (Orange)
    - 0-29: Poor Match (Red)
    """
    if score >= 70:
        return 'green', 'Great Match'
    elif score >= 50:
        return 'yellow', 'Good Match'
    elif score >= 30:
        return 'orange', 'Weak Match'
    else:
        return 'red', 'Poor Match'


# ============================================================================
# BACKWARDS COMPATIBILITY
# ============================================================================

def get_recommended_trips(user_profile, trips_queryset=None, destination=None, limit=None):
    """Wrapper for backwards compatibility - calls V3 implementation"""
    return get_recommended_trips_v3(user_profile, trips_queryset, destination, limit, debug=False)
