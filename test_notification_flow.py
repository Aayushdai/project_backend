"""
Test script to verify the notification and mark_as_read flow
"""
import os
import django
import json
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_companion.settings')
django.setup()

from django.contrib.auth.models import User
from apps.users.models import UserProfile
from apps.chat.models import Message
from apps.trips.models import Trip
from rest_framework_simplejwt.tokens import RefreshToken
import requests

BASE_URL = 'http://127.0.0.1:8000/api'

def get_or_create_test_users(count=2):
    """Create test users for testing"""
    users = []
    for i in range(count):
        username = f'testuser_notif_{i}'
        user, created = User.objects.get_or_create(
            username=username,
            defaults={'email': f'{username}@test.com', 'first_name': f'Test{i}', 'last_name': f'User{i}'}
        )
        profile, _ = UserProfile.objects.get_or_create(
            user=user,
            defaults={'bio': f'Test user {i}'}
        )
        users.append((user, profile))
        print(f"User {i}: {user.username}")
    return users

def get_token(user):
    """Get JWT token for a user"""
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)

def test_notification_flow():
    """Test the complete notification flow"""
    print("\n=== Setting up test data ===")
    users = get_or_create_test_users(2)
    sender_user, sender_profile = users[0]
    receiver_user, receiver_profile = users[1]
    
    sender_token = get_token(sender_user)
    receiver_token = get_token(receiver_user)
    
    headers_sender = {'Authorization': f'Bearer {sender_token}', 'Content-Type': 'application/json'}
    headers_receiver = {'Authorization': f'Bearer {receiver_token}', 'Content-Type': 'application/json'}
    
    print(f"Sender: {sender_user.username}")
    print(f"Receiver: {receiver_user.username}")
    
    print("\n=== Creating test messages ===")
    # Create messages directly in database
    messages = []
    for i in range(3):
        msg = Message.objects.create(
            sender=sender_profile,
            receiver=receiver_profile,
            content=f"Test message {i+1}",
            is_read=False
        )
        messages.append(msg)
        print(f"Created message {msg.id}: {msg.content}")
    
    print("\n=== Fetching unread messages for receiver ===")
    resp = requests.get(f'{BASE_URL}/chat/messages/unread_notifications/', headers=headers_receiver)
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        
        if data.get('results'):
            print(f"\nFound {len(data['results'])} messages")
            
            # Test mark_as_read for first message
            first_msg = data['results'][0]
            msg_id = first_msg['id']
            print(f"\n=== Testing mark_as_read for message {msg_id} ===")
            
            mark_read_resp = requests.patch(
                f'{BASE_URL}/chat/messages/{msg_id}/mark_as_read/',
                headers=headers_receiver
            )
            print(f"Mark as read status: {mark_read_resp.status_code}")
            if mark_read_resp.status_code == 200:
                marked_msg = mark_read_resp.json()
                print(f"Marked message: {json.dumps(marked_msg, indent=2)}")
                print(f"is_read: {marked_msg.get('is_read')}")
            else:
                print(f"Error: {mark_read_resp.text}")
            
            # Verify message is marked as read in database
            print(f"\n=== Verifying database state ===")
            db_msg = Message.objects.get(id=msg_id)
            print(f"Message {msg_id} is_read: {db_msg.is_read}")
            print(f"Message {msg_id} is_read_at: {db_msg.is_read_at}")
            
    else:
        print(f"Error: {resp.text}")
    
    print("\n=== Test complete ===")

if __name__ == '__main__':
    try:
        test_notification_flow()
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
