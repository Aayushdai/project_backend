# 📧 Email Notification System - Setup Guide

## Overview
Your Travel Companion backend now has a complete email notification system that sends emails for:
- User registration confirmation
- Password resets
- Trip invitations
- Expense notifications
- Travel buddy match notifications
- Expense settlement reminders
- KYC document submission confirmation
- KYC approval/rejection notifications

## Prerequisites
- Gmail account (or any email provider with SMTP support)
- Django environment with `django.core.mail` available

## Setup Instructions

### 1. Generate Gmail App Password
Since Gmail requires app-specific passwords for third-party applications:

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable **2-Step Verification** (if not already enabled)
3. Go back to Security settings and find **App passwords**
4. Select **Mail** and **Windows Computer** (or your platform)
5. Google will generate a 16-character password
6. **Copy this password** (you won't see it again)

### 2. Set Environment Variables
Create a `.env` file in your project root (Travel_Companion_Backend/):

```plaintext
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=xxxx xxxx xxxx xxxx
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

**Replace:**
- `your-email@gmail.com` with your Gmail address
- `xxxx xxxx xxxx xxxx` with the app password from step 1
- `noreply@yourdomain.com` with your preferred sender email

### 3. Install python-decouple (Recommended)
This library helps you load environment variables from `.env` file:

```bash
pip install python-decouple
```

### 4. Update settings.py (if using python-decouple)
Replace the EMAIL configuration in `travel_companion/settings.py` with:

```python
from decouple import config

# ========================
# EMAIL CONFIGURATION (Gmail SMTP)
# ========================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='your-email@gmail.com')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='your-app-password')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@travelcompanion.com')
```

### 5. Test Your Configuration
Run this management command to test email setup:

```bash
python manage.py shell
```

Then in the Python shell:

```python
from django.core.mail import send_mail

send_mail(
    'Test Subject',
    'This is a test email from Travel Companion.',
    'from@example.com',
    ['to@example.com'],
    fail_silently=False,
)
```

If no error occurs, your email configuration is working!

## How It Works

### Email Events Triggered Automatically

#### 1. User Registration
- **When:** New user account created
- **Location:** `apps/users/signals.py`
- **Recipient:** New user's email
- **Content:** Welcome message with next steps

#### 2. Trip Invitation
- **When:** User is added to a trip
- **Location:** Call `notify_trip_invitation()` from `apps/trips/email_helpers.py` in your view
- **Recipient:** Invited participant's email
- **Content:** Trip details and invitation to view/respond

#### 3. Expense Added
- **When:** New expense is created for a trip
- **Location:** Call `notify_trip_participants_expense()` from `apps/trips/email_helpers.py` after expense creation
- **Recipients:** All trip participants (except the one who added the expense)
- **Content:** Expense amount and trip name

#### 4. Travel Buddy Match
- **When:** New match found for user
- **Location:** Call `notify_new_match()` from `apps/users/email_helpers.py`
- **Recipient:** User receiving the match
- **Content:** Matched user name and compatibility score

#### 5. Expense Reminder
- **When:** User hasn't paid their share
- **Location:** Call `notify_settlement_reminder()` from `apps/expenses/email_helpers.py`
- **Recipient:** User who owes money
- **Content:** Amount owed and creditor name

#### 6. KYC Submission Confirmation
- **When:** User submits KYC documents
- **Location:** Call `notify_kyc_submission_confirmation()` from `apps/users/email_helpers.py`
- **Recipient:** User
- **Content:** Confirmation that documents were received and verification is in progress

#### 7. KYC Approval
- **When:** Admin approves KYC verification
- **Location:** Call `notify_kyc_approved()` from `apps/users/email_helpers.py` in your admin actions
- **Recipient:** User
- **Content:** Celebration of approval and access to full features

#### 8. KYC Rejection
- **When:** Admin rejects KYC verification
- **Location:** Call `notify_kyc_rejected()` from `apps/users/email_helpers.py` in your admin actions
- **Recipient:** User
- **Content:** Rejection reason and instructions to resubmit

## Integration Examples

### Example 1: Send Email When Adding Trip Participant

In `apps/trips/views.py`:

```python
from apps.trips.email_helpers import notify_trip_invitation

class TripDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    def perform_update(self, serializer):
        trip = serializer.save()
        
        # If new participants were added
        if 'participants' in self.request.data:
            new_participant_ids = self.request.data.get('participants')
            for participant_id in new_participant_ids:
                participant = UserProfile.objects.get(id=participant_id)
                notify_trip_invitation(participant, trip)
```

### Example 2: Send Email When Expense is Created

In `apps/expenses/views.py`:

```python
from apps.trips.email_helpers import notify_trip_participants_expense

class ExpenseListView(generics.ListCreateAPIView):
    def perform_create(self, serializer):
        expense = serializer.save()
        notify_trip_participants_expense(expense)
```

### Example 3: Send Email for New Match

In `apps/users/views_api.py`:

```python
from apps.users.email_helpers import notify_new_match

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def match_users(request):
    profile = request.user.userprofile
    matches = find_similar_users(profile)
    
    for user, similarity in matches:
        # Notify the matched user
        notify_new_match(user, profile.user.get_full_name(), similarity)
    
    # ... rest of the logic
```

## Module Overview

### `core/email_service.py`
Main email service with methods for all notification types. All email sending goes through this module for consistency and centralized management.

**Available Methods:**
- `send_registration_confirmation()`
- `send_password_reset_email()`
- `send_trip_invitation()`
- `send_expense_notification()`
- `send_match_notification()`
- `send_expense_reminder()`
- `send_kyc_submission_confirmation()`
- `send_kyc_approval_notification()`
- `send_kyc_rejection_notification()`

### `apps/users/email_helpers.py`
Helper functions for user-related events:
- `notify_new_match()`
- `notify_kyc_submission_confirmation()`
- `notify_kyc_approved()`
- `notify_kyc_rejected()`

### `apps/trips/email_helpers.py`
Helper functions for trip-related events:
- `notify_trip_invitation()`
- `notify_trip_participants_expense()`

### `apps/expenses/email_helpers.py`
Helper functions for expense-related events:
- `notify_settlement_reminder()`

## Troubleshooting

### Issue: "SMTPAuthenticationError"
**Cause:** Incorrect email credentials
**Solution:**
1. Verify your Gmail app password is correct
2. Ensure you've enabled 2-Step Verification on your account
3. Check that `.env` file has the correct values

### Issue: "SMTPException: SMTP AUTH extension not supported"
**Cause:** Port or TLS configuration issue
**Solution:**
- Verify `EMAIL_PORT = 587` (not 465 or 25)
- Ensure `EMAIL_USE_TLS = True`

### Issue: Emails aren't being sent but no errors
**Cause:** `fail_silently=True` is hiding errors
**Solution:**
- Temporarily set `fail_silently=False` in email_service.py to see actual errors
- Check Django logs

### Issue: Rate limiting from Gmail
**Cause:** Sending too many emails too quickly
**Solution:**
- Implement email queuing with Celery
- Add delays between emails if needed

## Production Considerations

### For Sending Large Volumes
Implement Celery task queue:

```bash
pip install celery redis
```

Then create `apps/users/tasks.py`:

```python
from celery import shared_task
from core.email_service import EmailService

@shared_task
def send_registration_email_task(user_email, username):
    EmailService.send_registration_confirmation(user_email, username)
```

### For Better Email Templates
Replace simple text with HTML templates using Django's template system:

```python
from django.template.loader import render_to_string

message = render_to_string('emails/registration.html', {'username': username})
send_mail(..., message=message, html_message=message)
```

### For Email Tracking
Use services like:
- **SendGrid** - Better deliverability and tracking
- **Mailgun** - Developer-friendly with excellent API
- **AWS SES** - Scalable for production

## Security Notes

✅ **DO:**
- Never commit `.env` file to git (add to `.gitignore`)
- Use environment variables for sensitive data
- Use app-specific passwords instead of main account password
- Enable 2-Step Verification on Gmail account

❌ **DON'T:**
- Don't hardcode email credentials in settings.py
- Don't use main Gmail password in app
- Don't commit secrets to repository
- Don't send sensitive information in emails

## Next Steps

1. ✅ Complete the Gmail setup from section "1. Generate Gmail App Password"
2. ✅ Create `.env` file with your credentials
3. ✅ Run the test email command
4. ✅ Integrate email helpers into your API views/signals
5. ✅ Test by creating a user account and checking your email

Happy emailing! 📧✨
