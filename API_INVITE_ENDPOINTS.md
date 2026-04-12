# Trip Invitation API Endpoints Integration Guide

## Overview
The TripInviteModal frontend component is now fully updated to use real API calls. You need to implement these Django REST endpoints to make the feature work end-to-end.

## Required API Endpoints

### 1. Generate Invite Link
**POST** `/api/trips/{id}/generate-invite-link/`

Creates a shareable invite link for a trip.

**Request Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Response (200 OK):**
```json
{
  "link": "http://localhost:3000/invite/ABC123XYZ",
  "code": "ABC123XYZ",
  "trip_id": 1,
  "created_by": 5
}
```

**Implementation Notes:**
- Only trip creator should be able to generate links
- Code should be unique, short, and URL-safe (alphanumeric)
- Should be stored in database for later validation
- Links should ideally expire after 30 days

---

### 2. List Trip Suggestions (Find Friends)
**GET** `/api/users/suggestions/?trip_id={trip_id}`

Returns list of users with similarity scores based on interests/profile matching.

**Request Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Response (200 OK):**
```json
[
  {
    "id": 2,
    "name": "John Doe",
    "email": "john@example.com",
    "avatar": "JD",
    "interests": ["Adventure", "Hiking", "Nature"],
    "similarity": 0.92,
    "is_already_member": false,
    "is_already_invited": false
  },
  {
    "id": 3,
    "name": "Jane Smith",
    "email": "jane@example.com",
    "avatar": "JS",
    "interests": ["Photography", "Travel"],
    "similarity": 0.78,
    "is_already_member": false,
    "is_already_invited": false
  }
]
```

**Implementation Notes:**
- Calculate similarity using cosine similarity on interests vectors
- Exclude current user
- Exclude already invited users
- Exclude already members
- Sort by similarity score (descending)
- Return [Similarity percentage * 100]
- Consider filtering by location/interests

---

### 3. Create/Send Invitation
**POST** `/api/trips/{id}/invitations/`

Sends an invitation to a user to join a trip.

**Request Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "user_id": 5,
  "role": "member"
}
```

**Response (201 Created):**
```json
{
  "id": 12,
  "trip_id": 1,
  "invited_user": {
    "id": 5,
    "name": "Alice Johnson",
    "email": "alice@example.com"
  },
  "invited_by": {
    "id": 2,
    "name": "Trip Creator",
    "email": "creator@example.com"
  },
  "status": "pending",
  "role": "member",
  "created_at": "2024-01-15T10:30:00Z",
  "accepted_at": null,
  "rejected_at": null
}
```

**Status Codes:**
- `201 Created` - Invitation sent successfully
- `400 Bad Request` - User already invited or is member
- `403 Forbidden` - Only trip creator can invite
- `404 Not Found` - Trip or user not found

**Implementation Notes:**
- Only trip creator can send invitations
- Cannot invite same user twice
- Cannot invite existing trip members
- Should send email notification to invited user
- Set status to "pending"

---

### 4. List Invitations for Trip
**GET** `/api/trips/{id}/invitations/`

Returns all pending invitations for a trip.

**Request Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Response (200 OK):**
```json
[
  {
    "id": 12,
    "trip_id": 1,
    "invited_user": {
      "id": 5,
      "name": "Alice Johnson",
      "email": "alice@example.com",
      "avatar": "AJ"
    },
    "invited_by": {
      "id": 2,
      "name": "Trip Creator"
    },
    "status": "pending",
    "role": "member",
    "created_at": "2024-01-15T10:30:00Z"
  },
  {
    "id": 13,
    "trip_id": 1,
    "invited_user": {
      "id": 6,
      "name": "Bob Smith",
      "email": "bob@example.com",
      "avatar": "BS"
    },
    "invited_by": {
      "id": 2,
      "name": "Trip Creator"
    },
    "status": "accepted",
    "role": "member",
    "created_at": "2024-01-14T14:20:00Z",
    "accepted_at": "2024-01-14T15:45:00Z"
  }
]
```

**Implementation Notes:**
- Return all invitations (pending, accepted, rejected)
- Only show if user is trip creator
- Return most recent first

---

### 5. Revoke Invitation
**DELETE** `/api/trips/{id}/invitations/{invitation_id}/`

Revokes a pending invitation.

**Request Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Response (204 No Content)**

**Status Codes:**
- `204 No Content` - Invitation revoked successfully
- `403 Forbidden` - Only trip creator can revoke
- `404 Not Found` - Invitation not found
- `400 Bad Request` - Cannot revoke accepted invitation

**Implementation Notes:**
- Only allow revoking pending invitations
- Only trip creator can revoke
- If invitation was accepted, cannot revoke

---

## Database Models Required

### TripInvitation Model
```python
class TripInvitation(models.Model):
    PENDING = 'pending'
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'
    
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (ACCEPTED, 'Accepted'),
        (REJECTED, 'Rejected'),
    ]
    
    ROLE_CHOICES = [
        ('member', 'Member'),
        ('organizer', 'Organizer'),
    ]
    
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='invitations')
    invited_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invitations_received')
    invited_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='invitations_sent')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    created_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    rejected_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ('trip', 'invited_user')  # Can't invite same user twice
        ordering = ['-created_at']
```

### TripInviteLink Model (for shareable links)
```python
class TripInviteLink(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='invite_links')
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    code = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        ordering = ['-created_at']
```

---

## Frontend Integration Status

✅ **COMPLETED:**
- TripInviteModal component fully built
- Share Link tab (copy-to-clipboard)
- Find Friends tab with similarity matching
- Pending invitations tracking
- Mobile responsive design
- Dark theme matching

🔄 **READY FOR API:**
- `generateInviteLink()` - POST endpoint ready
- `fetchSuggestedPeople()` - GET endpoint ready
- `handleInvitePerson()` - POST endpoint ready
- `fetchPendingInvitations()` - GET endpoint ready
- `revokeInvitation()` - DELETE endpoint ready

---

## Testing Checklist

After implementing endpoints:

1. **Generate Invite Link**
   - [ ] POST to `/api/trips/{id}/generate-invite-link/`
   - [ ] Verify unique code generated
   - [ ] Verify link structure matches frontend expectation
   - [ ] Test permission: only creator can generate

2. **Fetch Suggestions**
   - [ ] GET `/api/users/suggestions/?trip_id={id}`
   - [ ] Verify similarity scores calculated
   - [ ] Verify already-invited users excluded
   - [ ] Verify already-members excluded

3. **Send Invitation**
   - [ ] POST to `/api/trips/{id}/invitations/`
   - [ ] Verify invitation created with pending status
   - [ ] Verify can't invite twice
   - [ ] Verify email notification sent
   - [ ] Check permission: only creator can invite

4. **List Invitations**
   - [ ] GET `/api/trips/{id}/invitations/`
   - [ ] Verify returns all statuses
   - [ ] Verify latest first
   - [ ] Verify response structure matches frontend

5. **Revoke Invitation**
   - [ ] DELETE `/api/trips/{id}/invitations/{id}/`
   - [ ] Verify pending invitations can be revoked
   - [ ] Verify accepted invitations cannot be revoked
   - [ ] Verify permission check

---

## Error Handling

The frontend expects these error scenarios:

**400 Bad Request:**
```json
{
  "detail": "User already invited to this trip"
}
```

**403 Forbidden:**
```json
{
  "detail": "Only trip creator can perform this action"
}
```

**404 Not Found:**
```json
{
  "detail": "Trip not found"
}
```

---

## Email Notification Template (Optional)

When invitation is sent, consider sending email like:

**Subject:** You're invited to join a trip!

**Body:**
```
Hi {invited_user.name},

{creator.name} has invited you to join their trip "{trip.title}" 
scheduled for {trip.start_date} to {trip.end_date}.

[Accept Invite Button]
[Decline Invite Button]

Or visit: {frontend_url}/trips/{trip.id}
```

---

## Notes for Backend Implementation

1. All timestamps should be in UTC ISO format
2. Avatar field should be user's initials (e.g., "AJ" for Alice Johnson)
3. Similarity scores should be 0-100 (percentage)
4. Ensure proper pagination for large user lists
5. Add rate limiting to prevent spam invitations
6. Consider soft-delete for revoked invitations (audit trail)
