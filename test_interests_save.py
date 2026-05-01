#!/usr/bin/env python
"""
Quick test to verify interests are being saved correctly
Run from: Travel_Companion_Backend directory
python test_interests_save.py
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_companion.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth.models import User
from apps.users.models import UserProfile, Interest

# Get test user or create one
test_user, _ = User.objects.get_or_create(
    username='testuser',
    defaults={'email': 'test@test.com', 'first_name': 'Test', 'last_name': 'User'}
)

# Get or create profile
profile, _ = UserProfile.objects.get_or_create(
    user=test_user,
    defaults={'bio': 'Test bio', 'travel_style': 'adventure'}
)

# Get some interests (or create if needed)
interests = Interest.objects.all()[:3]
if not interests:
    print("❌ No interests found in database. Please seed the database first.")
    sys.exit(1)

print(f"✅ Test User: {test_user.username}")
print(f"✅ Profile: {profile}")
print(f"✅ Available interests: {[i.name for i in interests]}")

# Save interests
print(f"\n📝 Setting interests: {[i.id for i in interests]}")
profile.interests.set([i.id for i in interests])
profile.save()

# Verify saved
saved_interests = profile.interests.all()
print(f"✅ Saved interests count: {saved_interests.count()}")
print(f"✅ Saved interests: {[(i.id, i.name, i.category) for i in saved_interests]}")

if saved_interests.count() == interests.count():
    print("\n✅ TEST PASSED: Interests saved successfully!")
else:
    print("\n❌ TEST FAILED: Interest count mismatch!")
    sys.exit(1)
