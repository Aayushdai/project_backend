#!/usr/bin/env python
"""
Script to create a test user for debugging the login issue.
Run: python create_test_user.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_companion.settings')
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth import authenticate

print("=" * 60)
print("TEST USER CREATION & LOGIN DEBUG")
print("=" * 60)

# Check existing users
existing_users = User.objects.all()
print(f"\n📊 Current users in database: {existing_users.count()}")

if existing_users.count() > 0:
    print("\nExisting users:")
    for u in existing_users:
        print(f"  ✓ {u.username} - Active: {u.is_active}")

# Create test user
print("\n" + "-" * 60)
print("Creating test user...\n")

username = "testuser"
password = "testpass123"
email = "test@example.com"

# Delete existing test user if it exists
User.objects.filter(username=username).delete()

# Create new test user
test_user = User.objects.create_user(
    username=username,
    email=email,
    password=password
)

print(f"✓ Created test user:")
print(f"  Username: {username}")
print(f"  Password: {password}")
print(f"  Email: {email}")
print(f"  Is Active: {test_user.is_active}")

# Test authentication
print("\n" + "-" * 60)
print("Testing authentication...\n")

auth_user = authenticate(username=username, password=password)

if auth_user is not None:
    print(f"✓ Authentication SUCCESS!")
    print(f"  Authenticated user: {auth_user.username}")
else:
    print(f"❌ Authentication FAILED!")
    print(f"  The authenticate() function returned None")

# Test with wrong password
print("\n" + "-" * 60)
print("Testing with wrong password...\n")

wrong_auth = authenticate(username=username, password="wrongpassword")
if wrong_auth is None:
    print(f"✓ Correctly rejected wrong password (as expected)")
else:
    print(f"⚠️  Unexpectedly accepted wrong password!")

print("\n" + "=" * 60)
print("NEXT STEPS:")
print("=" * 60)
print(f"""
1. Try logging in with these credentials:
   Username: {username}
   Password: {password}

2. If login still fails with 401, check:
   - Browser DevTools > Network > Login request
   - Look at the request body - is it valid JSON?
   - Is username/password being sent correctly?

3. If login works, the issue was missing users in database.
   Create real user accounts or use admin panel.

4. To create a superuser:
   python manage.py createsuperuser

5. Full Django shell debug:
   python manage.py shell
   >>> from django.contrib.auth import authenticate
   >>> user = authenticate(username='testuser', password='testpass123')
   >>> print(user)
""")
