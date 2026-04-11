#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_companion.settings')
django.setup()

from apps.users.models import User, UserProfile

nepal_users = User.objects.filter(username__startswith='nepal_traveler_').count()
nepal_profiles = UserProfile.objects.filter(country='Nepal').count()

print(f'\n✅ NEPAL USERS POPULATION COMPLETE!\n')
print(f'📊 Total Nepal Users Created: {nepal_users}')
print(f'📊 Total Nepal Profiles: {nepal_profiles}')

# Check samples
nepal_user_objects = User.objects.filter(username__startswith='nepal_traveler_')
if nepal_user_objects.exists():
    print(f'\n📋 Sample Users:')
    for i, u in enumerate(nepal_user_objects[:3]):
        has_profile = hasattr(u, 'userprofile')
        if has_profile:
            profile = u.userprofile
            print(f'\n   User {i+1}: {u.first_name} {u.last_name} (@{u.username})')
            print(f'   Location: {profile.location}')
            print(f'   Budget: {profile.budget_level}/10 | Adventure: {profile.adventure_level}/10 | Social: {profile.social_level}/10')
            print(f'   Interests: {profile.interests.count()} | Tags: {profile.constraint_tags.count()}')

print(f'\n✨ Ready for cosine similarity matching! 🚀\n')

