# Populate User Interests & Tags Guide

## What This Does

This Django management command adds travel interests and constraint tags to all your users so that the cosine similarity matching system can work properly.

## For Each User It Creates:

✅ **3-5 Travel Interests** (randomly assigned from):
- Activities: Hiking, Photography, Cultural Tours, Beach Activities, Nightlife, Food & Cuisine, Adventure Sports, Museums, Wildlife, Yoga
- Destinations: Mountains, Beaches, Cities, Rural Areas, Islands, Deserts, Jungles, Historical Sites
- Experiences: Budget Travel, Luxury Travel, Solo Travel, Group Travel, Family Travel, Backpacking

✅ **2-4 Constraint Tags** (randomly assigned from):
- Diet: Vegetarian, Vegan, Non-Vegetarian
- Lifestyle: Non-Smoker, Smoker, Non-Drinker, Social Drinker
- Values: Eco-Conscious, Animal Lover, Adventure Seeker, Relaxation Focused, Cultural Explorer

✅ **Travel Preferences**:
- Travel Style: Budget / Luxury / Adventure
- Pace: Relaxed / Moderate / Fast-paced
- Accommodation: Hostel / Hotel / Inn / Camping

✅ **Experience Scores** (1-10):
- Budget Level: How budget-conscious (1=expensive, 10=very cheap)
- Adventure Level: How adventurous (1=stay safe, 10=extreme)
- Social Level: How social (1=solo, 10=very social)

✅ **Date of Birth** (for age compatibility checks)

## How to Run

### 1. Navigate to Django project
```bash
cd c:\Users\Aayush\Desktop\chatbot\Travel_Companion_Backend
```

### 2. Activate Python environment
```bash
# On Windows PowerShell
.\..\chatbot\Scripts\Activate.ps1

# Or on PowerShell in repo
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Run the management command
```bash
python manage.py populate_user_interests
```

## Expected Output

```
✅ Created Interest: Hiking (activity)
✅ Created Interest: Photography (activity)
...
✅ Created Constraint Tag: Vegetarian (diet)
...

📝 Assigning interests to 17 users...

✅ a@gail.com
   Interests: Hiking, Photography, Beach Activities
   Tags: Vegetarian, Non-Smoker, Eco-Conscious
   Travel Style: adventure, Pace: fast_paced
   Scores: Budget=7, Adventure=8, Social=6

✅ aayush
   Interests: Cultural Tours, Food & Cuisine, Meditation & Yoga
   Tags: Non-Vegetarian, Social Drinker, Adventure Seeker
...

✅ Successfully populated 17 users with interests and constraint tags!
Now you can use cosine similarity matching to find travel buddies! 🚀
```

## What Happens Next

After running this command:

1. **All users will have tags** → Cosine similarity can now compare them
2. **Travel buddy matching will work** → `find_similar_users()` will find actual matches
3. **Similar scores will be calculated** → Users with matching interests/tags get higher scores

## How Similarity Matching Works

The system now does:

### Hard Filters (Must Pass):
- ✅ Age compatibility (within min_match_age to max_match_age)
- ✅ Critical constraint compatibility (vegetarian ≠ meat-eaters in strict mode)

### Soft Matching (Cosine Similarity):
- Travel style compatibility
- Budget/adventure/social score similarity
- **Interest overlap** (shared activities, destinations, experiences)
- **Constraint tag alignment** (similar diet, lifestyle, values)

Higher similarity scores = Better travel buddy matches!

## Example Matching

**User A** (aayush):
- Interests: Hiking, Photography, Mountains
- Tags: Non-Smoker, Adventure Seeker, Eco-Conscious
- Scores: Budget=7, Adventure=9, Social=7

**User B** (giga):
- Interests: Hiking, Camping, Mountains  
- Tags: Non-Smoker, Adventure Seeker, Animal Lover
- Scores: Budget=6, Adventure=8, Social=7

**Result**: High similarity score (~0.85) = Excellent match! 🎯

## Fine-Tuning

If you want to manually adjust interests later:

```python
from apps.users.models import UserProfile, Interest

user = UserProfile.objects.get(user__username='aayush')
hiking = Interest.objects.get(name='Hiking')

# Add interest
user.interests.add(hiking)

# Remove interest
user.interests.remove(hiking)

# View interests
print(user.interests.all())
```

---

**Need help?** Check the logs in the terminal to see what was created and assigned!
