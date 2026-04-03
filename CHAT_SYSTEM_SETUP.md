# Backend Chat System Setup Checklist

## Current Implementation Status

### ✅ Completed
- `Message` model defined in `apps/chat/models.py`
- `MessageSerializer` created with all required fields
- `MessageViewSet` with `create()`, `direct_messages()`, and `group_messages()` actions
- URL routes added in `apps/chat/urls_new.py`
- Validation for both direct and group messages
- Friend and trip member checks

### ⚠️ Configuration Required

## Step 1: Verify URL Routing

**File**: `Travel_Companion_Backend/travel_companion/urls.py`

Ensure the chat URLs are included in main urlpatterns:
```python
urlpatterns = [
    # ... other patterns
    path('chat/api/', include('apps.chat.urls_new')),
]
```

If using `urls.py` instead of `urls_new.py`, update it accordingly:
```python
router = DefaultRouter()
router.register(r'chat', ChatViewSet, basename='chat')
router.register(r'messages', MessageViewSet, basename='messages')

urlpatterns = [
    path('', include(router.urls)),
]
```

## Step 2: Database Migrations

Run these commands:
```bash
cd Travel_Companion_Backend

# Generate migration if model hasn't been migrated
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

## Step 3: Verify API Endpoints

After running the server, test these endpoints:

### Get Direct Messages
```
GET /chat/api/messages/direct_messages/?recipient_id=2
Authorization: Bearer {access_token}
```

Response:
```json
[
  {
    "id": 1,
    "sender": 1,
    "sender_name": "John Doe",
    "receiver": 2,
    "receiver_name": "Jane Smith",
    "trip": null,
    "trip_name": null,
    "content": "Hello!",
    "timestamp": "2024-04-03T10:30:00Z",
    "isSent": true,
    "created_at": "2024-04-03T10:30:00Z"
  }
]
```

### Get Group Messages
```
GET /chat/api/messages/group_messages/?trip_id=5
Authorization: Bearer {access_token}
```

### Send Direct Message
```
POST /chat/api/messages/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "content": "Your message here",
  "receiver_id": 2
}
```

### Send Group Message
```
POST /chat/api/messages/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "content": "Group message text",
  "trip_id": 5
}
```

## Step 4: Test with Frontend

1. **Start the development server**:
```bash
cd Travel_Companion_Backend
python manage.py runserver
```

2. **Start React app**:
```bash
cd travel-companion-frontend
npm start
```

3. **Create test data**:
   - Create 2+ test users
   - Mark them as KYC approved
   - Add them as friends in the app
   - Create a trip and add multiple members

4. **Test Chat Flow**:
   - Log in as User A
   - Navigate to Chat tab
   - Verify conversations list loads
   - Open a direct message conversation
   - Send a test message
   - Log in as User B (different browser/incognito)
   - Verify message appears after 3-second refresh
   - Send a reply
   - Verify User A sees the message

## Step 5: Enable CORS (if needed)

If frontend and backend are on different domains, verify CORS is properly configured:

**File**: `Travel_Companion_Backend/travel_companion/settings.py`

```python
INSTALLED_APPS = [
    # ...
    'corsheaders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Must be before Django middleware
    # ... other middleware
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    # Add your frontend domain
]

CORS_ALLOW_CREDENTIALS = True
```

## API Response Format

### Success Response (201 Created)
```json
{
  "id": 1,
  "sender": 1,
  "sender_name": "John Doe",
  "receiver": 2,
  "receiver_name": "Jane Smith",
  "trip": null,
  "trip_name": null,
  "content": "Hello there!",
  "timestamp": "2024-04-03T10:35:00Z",
  "isSent": true,
  "created_at": "2024-04-03T10:35:00Z"
}
```

### Error Responses

**Empty Content (400)**:
```json
{
  "error": "Message content cannot be empty"
}
```

**User Not Member of Trip (403)**:
```json
{
  "error": "You are not a member of this trip"
}
```

**Recipient Not Found (404)**:
```json
{
  "error": "Receiver not found"
}
```

## Troubleshooting

### Issue: "User profile not found"
**Solution**: Ensure UserProfile is created when User is created. Check signals or user creation logic.

### Issue: Messages not appearing
**Solution**: 
- Check browser network tab for fetch errors
- Verify auth token in localStorage
- Ensure backend is running at http://127.0.0.1:8000
- Check CORS configuration

### Issue: "Not a member of this trip"
**Solution**: Verify the user is in the trip's members list. Check the Trip model's members relationship.

### Issue: 404 on message endpoint
**Solution**: Verify the chat app is included in main `urls.py` with correct path prefix.

## Performance Notes

### Current Implementation
- **Polling**: Messages refresh every 3 seconds
- **Database Queries**: O(n) where n = number of messages with that user
- **No pagination**: All messages loaded at once (limit for large conversations)

### Future Optimizations
1. Implement WebSocket for real-time updates
2. Add message pagination (load first 50, then on scroll)
3. Add database indexing on (sender, receiver) and (trip) fields
4. Add caching for conversations list
5. Implement lazy-loading message history

## Database Indexes to Add (Optional but Recommended)

```python
class Message(models.Model):
    # ... fields ...
    
    class Meta:
        indexes = [
            models.Index(fields=['sender', 'receiver'], name='direct_msg_idx'),
            models.Index(fields=['trip'], name='group_msg_idx'),
            models.Index(fields=['timestamp'], name='timestamp_idx'),
        ]
```

## Frontend Testing Checklist

- [ ] Chat tab appears in sidebar
- [ ] Conversations load when clicking Chat tab
- [ ] Can click conversation to open thread
- [ ] Messages display with timestamps
- [ ] Can type and send messages
- [ ] Sent messages appear immediately
- [ ] Received messages appear within 3-5 seconds
- [ ] Back button returns to conversations list
- [ ] Error messages display on failed sends
- [ ] Loading spinner shows while fetching
- [ ] Input field disables while sending
- [ ] Enter key sends message
- [ ] Multiple conversations work independently
- [ ] Group messages show trip members count
- [ ] Direct messages show friend name/avatar

## Next Steps

1. ✅ Frontend implementation - DONE
2. ✅ Backend serializers & viewsets - DONE
3. ⏳ Test with actual backend running
4. ⏳ Implement WebSocket for real-time (future)
5. ⏳ Add message notifications (future)
6. ⏳ Add typing indicators (future)