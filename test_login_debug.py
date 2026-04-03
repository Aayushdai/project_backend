#!/usr/bin/env python
"""
Debug script to test login authentication issue.
Run from Django shell: python manage.py shell < test_login_debug.py
"""

import django
import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_companion.settings')
django.setup()

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from apps.users.models import UserProfile

print("=" * 60)
print("LOGIN AUTHENTICATION DEBUG SCRIPT")
print("=" * 60)

# Check all users in database
print("\n1. CHECKING ALL USERS IN DATABASE:")
print("-" * 60)
all_users = User.objects.all()
if all_users.count() == 0:
    print("❌ NO USERS FOUND! You need to create a user first.")
else:
    print(f"✓ Found {all_users.count()} user(s):\n")
    for user in all_users:
        print(f"  Username: {user.username}")
        print(f"  Email: {user.email}")
        print(f"  Is Active: {user.is_active}")
        print(f"  Has UserProfile: {hasattr(user, 'userprofile')}")
        print()

# Test authentication with first user (if exists)
print("\n2. TESTING AUTHENTICATION:")
print("-" * 60)
if all_users.count() > 0:
    test_user = all_users.first()
    test_username = test_user.username
    
    print(f"Testing with username: {test_username}")
    print(f"NOTE: You need to know the correct password for this user!")
    
    # Try to authenticate
    print("\n⚠️  Manual test:")
    print("  In Django shell, run:")
    print(f"  from django.contrib.auth import authenticate")
    print(f"  user = authenticate(username='{test_username}', password='YOUR_PASSWORD')")
    print(f"  print(user)  # Should print User object, not None")
    print(f"\nIf result is None, the password is wrong.")
    print(f"If result shows User object, authentication works!")
    
else:
    print("❌ Cannot test - no users exist in database yet.")
    print("\n   CREATE A TEST USER:")
    print("   python manage.py createsuperuser")
    print("   OR in Django shell:")
    print("   from django.contrib.auth.models import User")
    print("   User.objects.create_user(username='testuser', password='testpass123')")

# Check Django settings
print("\n3. CHECKING DJANGO CONFIGURATION:")
print("-" * 60)
from django.conf import settings
print(f"DEBUG: {settings.DEBUG}")
print(f"AUTHENTICATION_BACKENDS: {settings.AUTHENTICATION_BACKENDS}")
print(f"INSTALLED_APPS: {[app for app in settings.INSTALLED_APPS if 'auth' in app.lower() or 'user' in app.lower()]}")

print("\n" + "=" * 60)
print("TROUBLESHOOTING STEPS:")
print("=" * 60)
print("""
1. Check if user exists and credentials are correct:
   - Try logging in with a known username/password
   - Verify the password is correct

2. Create a test user if none exists:
   python manage.py createsuperuser
   
3. Test authentication directly in Django shell:
   python manage.py shell
   >>> from django.contrib.auth import authenticate
   >>> user = authenticate(username='yourusername', password='yourpassword')
   >>> print(user)  # Should print User object, not None
   
4. Check if user is active:
   python manage.py shell
   >>> from django.contrib.auth.models import User
   >>> user = User.objects.get(username='yourusername')
   >>> print(user.is_active)  # Should be True

5. Verify the frontend is sending correct credentials:
   - Check browser DevTools > Network > Login request
   - See if the body contains correct username and password JSON
""")
