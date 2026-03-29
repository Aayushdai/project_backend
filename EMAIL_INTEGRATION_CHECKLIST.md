# Email Integration Checklist

Complete these steps to fully integrate email notifications into your views and admin panels.

## ✅ Backend Setup (Already Complete)
- [x] Created email service module (`core/email_service.py`)
- [x] Updated Django settings with email configuration
- [x] Created email helper functions for each app
- [x] Setup registration confirmation email (via signals)
- [x] Created `.env.example` file
- [x] Created setup documentation

## 📋 Integration Tasks (TODO)

### 1. Trip Invitations
**Status:** ⏳ Needs Implementation
**Files to Update:** `apps/trips/views.py`

```python
# Add this import at the top
from apps.trips.email_helpers import notify_trip_invitation

# In your trip update view or participant addition view:
def add_participant(request):
    # ... your logic to add participant ...
    participant = UserProfile.objects.get(id=participant_id)
    trip = Trip.objects.get(id=trip_id)
    notify_trip_invitation(participant, trip)
```

### 2. Expense Notifications
**Status:** ⏳ Needs Implementation
**Files to Update:** `apps/expenses/views.py`

```python
# Add this import at the top
from apps.trips.email_helpers import notify_trip_participants_expense

# In your expense creation view:
class ExpenseListView(generics.ListCreateAPIView):
    def perform_create(self, serializer):
        expense = serializer.save()
        notify_trip_participants_expense(expense)  # Add this line
```

### 3. Travel Buddy Match Notifications
**Status:** ⏳ Needs Implementation
**Files to Update:** `apps/users/views_api.py`

```python
# Add this import at the top
from apps.users.email_helpers import notify_new_match

# In your match_users view:
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def match_users(request):
    profile = request.user.userprofile
    matches = find_similar_users(profile)
    
    result = []
    for user, similarity in matches:
        # Add email notification
        notify_new_match(user, profile.user.get_full_name() or profile.user.username, similarity)
        
        result.append({
            "username": user.user.username,
            "similarity": similarity
        })
    
    return Response(result)
```

### 4. KYC Notifications (Admin)
**Status:** ⏳ Needs Implementation
**Files to Update:** `apps/users/admin.py` or `core/admin.py`

For KYC approval/rejection emails, add custom admin actions:

```python
from apps.users.email_helpers import notify_kyc_approved, notify_kyc_rejected

class KYCProfileAdmin(admin.ModelAdmin):
    actions = ['approve_kyc', 'reject_kyc']
    
    def approve_kyc(self, request, queryset):
        for kyc_profile in queryset:
            kyc_profile.status = 'approved'
            kyc_profile.save()
            notify_kyc_approved(kyc_profile.user)
        self.message_user(request, "KYC approved and notifications sent")
    
    def reject_kyc(self, request, queryset):
        for kyc_profile in queryset:
            reason = request.POST.get('rejection_reason', 'Documents do not meet requirements')
            kyc_profile.status = 'rejected'
            kyc_profile.save()
            notify_kyc_rejected(kyc_profile.user, reason)
        self.message_user(request, "KYC rejected and notifications sent")
```

### 5. Expense Settlement Reminders (Optional - Scheduled Task)
**Status:** ⏳ Optional, Needs Implementation
**Requires:** Celery + Redis or APScheduler

This can be triggered periodically to remind users of pending expenses.

## 🔧 Environment Setup

- [ ] Create `.env` file in `Travel_Companion_Backend/` folder
- [ ] Copy values from `.env.example`
- [ ] Add your Gmail email and app password
- [ ] Add `.env` to `.gitignore` (don't commit secrets!)
- [ ] Install `python-decouple`: `pip install python-decouple`

## ✨ Testing

1. **Test Registration Email:**
   - Create a new user account
   - Check email inbox for confirmation message
   - Verify it contains welcome message

2. **Test Trip Invitation:**
   - Create a trip
   - Add a participant
   - Check their email inbox
   - Verify it contains trip name and ID

3. **Test Expense Notification:**
   - Add an expense to a trip with multiple participants
   - Check email of other participants
   - Verify they receive expense amount and trip name

4. **Test Match Notification:**
   - Call the match_users endpoint
   - Check email of matched users
   - Verify they receive matched user name and score

## 🚀 Deployment

For production:
- [ ] Use environment variables from your hosting platform (Heroku, AWS, etc.)
- [ ] Don't use `.env` file in production
- [ ] Consider using SendGrid, Mailgun, or AWS SES instead of Gmail
- [ ] Implement Celery for async email sending
- [ ] Add email templates using Django's template system
- [ ] Monitor email delivery rates

## 📞 Support

If you encounter issues:
1. Check `EMAIL_SETUP_GUIDE.md` for troubleshooting
2. Enable debug logging to see email details
3. Test with a simple test email command
4. Verify `.env` file is in the correct location

## 📁 Files Modified/Created

- ✅ `core/email_service.py` - Main email service
- ✅ `apps/users/signals.py` - Registration email trigger
- ✅ `apps/users/email_helpers.py` - User event helpers
- ✅ `apps/trips/email_helpers.py` - Trip event helpers
- ✅ `apps/expenses/email_helpers.py` - Expense event helpers
- ✅ `travel_companion/settings.py` - Email configuration added
- ✅ `.env.example` - Example environment variables
- ✅ `EMAIL_SETUP_GUIDE.md` - Complete setup documentation

## Next Steps

1. Complete the environment setup
2. Follow the integration tasks in order
3. Test each feature
4. Deploy and monitor email delivery
