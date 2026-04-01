#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_companion.settings')
django.setup()

from django.contrib.auth.models import User
from apps.kyc.models import KYCProfile

# Test: Create a test user and see if KYC profile is auto-created
test_email = 'test_signal@example.com'

# Clean up if it exists
User.objects.filter(email=test_email).delete()

print(f"Creating test user: {test_email}")
user = User.objects.create_user(
    username=test_email,
    email=test_email,
    password='testpass123'
)
print(f"User created: {user}")

# Check if KYC was auto-created
try:
    kyc = user.kyc_profile
    print(f"✓ KYC profile AUTO-CREATED: {kyc.status}")
except User.kyc_profile.RelatedObjectDoesNotExist:
    print(f"✗ KYC profile NOT auto-created")
    print("Signal is NOT firing!")
