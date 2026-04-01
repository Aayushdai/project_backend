#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_companion.settings')
django.setup()

from apps.kyc.models import KYCProfile

pending = KYCProfile.objects.filter(status='pending')
print(f'✓ Pending KYC profiles: {pending.count()}')
print("\nFirst 5 pending KYC profiles:")
for kyc in pending[:5]:
    print(f'  - {kyc.user.email}: {kyc.status}')
