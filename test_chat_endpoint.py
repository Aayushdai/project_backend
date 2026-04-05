import os
import django
import json
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_companion.settings')
django.setup()

from django.contrib.auth.models import User
from apps.users.models import UserProfile
from rest_framework_simplejwt.tokens import RefreshToken
import requests

# Create a test user
test_username = 'testbot123'
user, created = User.objects.get_or_create(
    username=test_username,
    defaults={'email': 'testbot@test.com'}
)
print(f"User: {user.username} (created={created})")

# Ensure user profile exists
userprofile, profile_created = UserProfile.objects.get_or_create(
    user=user,
    defaults={'bio': 'Test user'}
)
print(f"UserProfile: created={profile_created}")

# Get JWT token
refresh = RefreshToken.for_user(user)
access_token = str(refresh.access_token)
print(f"Token: {access_token[:20]}...")

# Test the endpoint
headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}
data = {'message': 'hello'}
resp = requests.post('http://127.0.0.1:8000/api/chat/chat/', json=data, headers=headers)
print(f"\nResponse Status: {resp.status_code}")
print(f"Response Text: {resp.text}")
try:
    print(f"Response JSON: {json.dumps(resp.json(), indent=2)}")
except:
    print("Could not parse response as JSON")

