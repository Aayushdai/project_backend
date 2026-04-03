#!/usr/bin/env python
"""Verify KYC and available trips"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_companion.settings')
django.setup()

from django.contrib.auth.models import User
from apps.trips.models import Trip
from datetime import date

user = User.objects.get(username='aayush')
kyc = user.kyc_profile

print('=== VERIFICATION ===')
print(f'User: {user.username}')
print(f'KYC Status: {kyc.status}')
print(f'Is KYC Approved: {kyc.status == "approved"}')

print('\n=== AVAILABLE TRIPS TO JOIN ===')
today = date.today()
available_trips = Trip.objects.filter(end_date__gte=today, is_public=True)

for trip in available_trips:
    is_participant = trip.participants.filter(id=user.userprofile.id).exists()
    status = '✓ JOINED' if is_participant else '○ CAN JOIN'
    print(f'{status} | Trip ID {trip.id}: {trip.title}')
    print(f'       Dates: {trip.start_date} to {trip.end_date}')
