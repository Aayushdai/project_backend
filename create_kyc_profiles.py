#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_companion.settings')
django.setup()

from django.contrib.auth.models import User
from apps.kyc.models import KYCProfile

# Get all users without KYC profiles
users_without_kyc = User.objects.filter(kyc_profile__isnull=True)
created_count = 0

print(f"Found {users_without_kyc.count()} users without KYC profiles\n")

for user in users_without_kyc:
    kyc, created = KYCProfile.objects.get_or_create(user=user)
    if created:
        created_count += 1
        print(f'✓ Created KYC for {user.email}')

print(f'\n{"="*50}')
print(f'Total KYC profiles created: {created_count}')
print(f'Total KYC profiles in system: {KYCProfile.objects.count()}')
print(f'Pending KYC: {KYCProfile.objects.filter(status="pending").count()}')
print(f'{"="*50}')
