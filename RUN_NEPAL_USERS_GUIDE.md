# 🇳🇵 Nepali Users Population Script

## ✨ What This Creates

- **100 Realistic Nepali Users** with:
  - Real Nepali cities & towns (Kathmandu, Pokhara, Everest regions, etc.)
  - Authentic Nepali addresses & locations
  - Diverse interests (10 different travel personas)
  - Constraint tags for strict matching (diet, lifestyle, values, age)
  - Random travel preferences (style, pace, accommodation)
  - Varied buddy scores (budget, adventure, social levels)

## 🚀 How to Run

### Step 1: Activate Your Virtual Environment

```bash
# Windows
cd c:\Users\Aayush\Desktop\chatbot\Travel_Companion_Backend
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### Step 2: Run the Population Script

```bash
python manage.py populate_nepal_users
```

### OR Create This Script First

If the script doesn't exist, create it with:

```bash
python manage.py populate_test_data
```

This will populate:
- ✅ Basic interests
- ✅ Constraint tags
- ✅ Base test users

Then run:

```bash
python manage.py populate_nepal_users
```

## 📊 What Gets Created

### Users & Profiles
- 100 users named `nepal_traveler_1` ... `nepal_traveler_100`
- First names: Nepali names (Arun, Bishan, Chandra, Anita, Binita, etc.)
- Last names: Nepali surnames (Khadka, Rai, Sherpa, Sharma, Poudel, etc.)

### Realistic Locations

**Kathmandu Valley:**
- Thamel, Bhaktapur, Patan, Swayambhunath, Boudhanath, Pashupatinath, etc.

**Pokhara Region:**
- Lakeside, Damside, Fewa, Sarankot, etc.

**Mountain Towns:**
- Namche Bazaar, Lukla, Ilam, Janakpur, Birgunj, etc.

**Western & Eastern:**
- Nepalgunj, Butwal, Itahari, Damak, Dharan, etc.

### Interests (10 Personas)
1. **Adventure Seeker** → Hiking, Rock Climbing, Mountains, Adventure Sports, Wildlife
2. **Cultural Explorer** → Cultural Immersion, Museum, Food Tours, Cities
3. **Food Lover** → Food Tours, Cooking, Cities, Cultural Immersion
4. **Nature Photographer** → Photography, Mountains, Forests, Wildlife
5. **Budget Backpacker** → Cycling, Beach, Budget Conscious, Hostels
6. **Luxury Traveler** → Beaches, Nightlife, Hotels, Cities
7. **Spiritual Soul** → Yoga, Mountains, Meditation, Cultural Immersion
8. **Sports Enthusiast** → Adventure Sports, Diving, Surfing, Cycling
9. **Urban Explorer** → Cities, Nightlife, Museums, Food Tours
10. **Nature Lover** → Forests, Mountains, Beaches, Wildlife

### Constraint Tags (15 Combinations)
Realistic combinations like:
- Vegetarian + Non-Smoker + Eco-conscious
- Non-Vegetarian + Non-Smoker + Fitness Focused
- Vegetarian + Social Drinker + Budget Conscious
- Vegan + Non-Smoker + Eco-conscious
- Halal + Non-Smoker + Budget Conscious
- And 10 more!

Each user also gets an **Age Range** (18-25, 25-35, 35-50, or 50+)

### Travel Preferences
- **Style:** Budget, Luxury, or Adventure
- **Pace:** Relaxed, Moderate, or Fast-paced
- **Accommodation:** Hostel, Hotel, Inn, or Camping
- **Buddy Scores:** Random 1-10 for Budget, Adventure, Social levels

## 💡 Why This Is Perfect For Testing

✅ **Diverse Personas** - 10 different interest combinations means varied matches
✅ **Constraint Tags** - Tests strict matching (no conflicts)
✅ **Real Locations** - Kathmandu-focused with spread across Nepal
✅ **Accurate Addresses** - Looks like real user data (for demo purposes)
✅ **Age Ranges** - Tests matching by age preferences
✅ **Varied Scores** - Tests cosine similarity on preference vectors

## 🎯 Expected Output

```
🇳🇵 Starting Nepali User Population...
✓ Created 10 users...
✓ Created 20 users...
✓ Created 30 users...
✓ Created 40 users...
✓ Created 50 users...
✓ Created 60 users...
✓ Created 70 users...
✓ Created 80 users...
✓ Created 90 users...
✓ Created 100 users...

✅ Successfully created 100 Nepali travel buddies!
⏭️  Skipped 0 existing users

📊 Total Users in System: 100
📊 Total Profiles: 100

✨ Your cosine similarity algorithm can now match travel buddies accurately! 🚀

💡 Features tested:
   • 100 diverse user personas
   • Realistic Nepali locations & addresses
   • Varied constraint tags for strict matching
   • Random travel preferences
   • Ages 20-50 with varied interests
```

## 🔍 Verify the Data

Check what was created:

```bash
python manage.py shell
```

Then in the shell:

```python
from apps.users.models import UserProfile
from django.contrib.auth.models import User

# Count users from Nepal
nepal_users = UserProfile.objects.filter(country="Nepal").count()
print(f"Nepal users: {nepal_users}")

# Check a sample user
sample = UserProfile.objects.filter(country="Nepal").first()
print(f"Sample user: {sample.user.first_name} {sample.user.last_name}")
print(f"Location: {sample.location}")
print(f"Address: {sample.address}")
print(f"Interests: {sample.interests.count()}")
print(f"Tags: {sample.constraint_tags.count()}")
```

## 🧬 Using for Cosine Similarity Testing

Now that you have 100 diverse users, you can test:

```python
# Test similarity matching
from apps.users.models import UserProfile
from django.contrib.auth.models import User

# Get a Nepal user
user1 = UserProfile.objects.filter(country="Nepal").first()

# Calculate similarity with others
# (Assuming you have a similarity function)
matches = calculate_similarity_matches(user1, top_n=10)
print(f"Top 10 matches for {user1.user.first_name}:")
for match_user, score in matches:
    print(f"  • {match_user.user.first_name}: {score}%")
```

## 📝 Notes

- All test users have password: `testpass123`
- All are marked as KYC approved (`status='approved'`)
- Emails follow pattern: `nepal_traveler_X@travelsathi.com`
- Phone numbers are formatted: `+977-XXXXXXXXXX` (valid Nepal format)
- Can be deleted anytime with: `User.objects.filter(username__startswith='nepal_traveler_').delete()`

---

**Ready to match travel buddies? 🌍✈️**
