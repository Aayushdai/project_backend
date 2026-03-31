#!/usr/bin/env python
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_companion.settings')
django.setup()

from django.contrib.auth.models import User
from apps.users.models import UserProfile

print('=' * 50)
print('USER PROFILE CHECK')
print('=' * 50)

total_users = User.objects.count()
total_profiles = UserProfile.objects.count()

print(f'\nTotal Users: {total_users}')
print(f'Total Profiles: {total_profiles}')

print('\n' + '=' * 50)
print('USERS WITH THEIR PROFILE STATUS:')
print('=' * 50)

for user in User.objects.all():
    try:
        profile = user.userprofile
        print(f'✓ {user.username} ({user.email}) - Profile ID: {profile.id}')
    except UserProfile.DoesNotExist:
        print(f'✗ {user.username} ({user.email}) - NO PROFILE')

print('\n' + '=' * 50)
users_without_profiles = User.objects.filter(userprofile__isnull=True)
if users_without_profiles.exists():
    print(f'\n⚠️  FOUND {users_without_profiles.count()} USER(S) WITHOUT PROFILE!')
    print('\nCreating missing profiles...')
    for user in users_without_profiles:
        profile = UserProfile.objects.create(user=user)
        print(f'✓ Created profile for {user.username}')
    print('\n✅ All missing profiles created!')
else:
    print('\n✅ All users have profiles!')
