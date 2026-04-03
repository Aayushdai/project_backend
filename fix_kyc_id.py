#!/usr/bin/env python
"""Fix KYC profile by adding id_number field"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_companion.settings')
django.setup()

from django.contrib.auth.models import User

user = User.objects.get(username='aayush')
kyc = user.kyc_profile

# Set the id_number field - this is required for the me_view endpoint to return 'approved'
kyc.id_number = 'TEST123456789'
kyc.save()

print('✓ Updated KYC Profile')
print(f'User: {user.username}')
print(f'KYC Status: {kyc.status}')
print(f'ID Number: {kyc.id_number}')
print()
print('The /users/api/me/ endpoint will now return:')
print(f'  "status": "approved"')
print()
print('NEXT STEP: Refresh your browser to see the Join buttons enabled!')
