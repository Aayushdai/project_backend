"""
Email notification templates and services for Travel Companion
Handles all email communications for user events
"""

from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string


class EmailService:
    """Service to handle all email notifications"""
    
    @staticmethod
    def send_registration_confirmation(user_email, username):
        """Send registration confirmation email"""
        subject = "Welcome to Travel Companion! 🌍"
        message = f"""
Hi {username},

Thank you for registering with Travel Companion!

Your account has been successfully created. You can now log in and start planning your trips with fellow travelers.

Getting Started:
1. Complete your profile with travel preferences
2. Explore travel buddies using our matching system
3. Create your first trip and start planning!

Best regards,
Travel Companion Team
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user_email],
            fail_silently=False,
        )
    
    @staticmethod
    def send_password_reset_email(user_email, username, reset_link):
        """Send password reset email"""
        subject = "Password Reset Request - Travel Companion"
        message = f"""
Hi {username},

You requested to reset your password. Click the link below to set a new password:

{reset_link}

This link will expire in 24 hours.

If you didn't request this, you can ignore this email.

Best regards,
Travel Companion Team
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user_email],
            fail_silently=False,
        )
    
    @staticmethod
    def send_trip_invitation(recipient_email, recipient_name, trip_creator, trip_name, trip_id):
        """Send trip invitation email"""
        subject = f"You're invited to join '{trip_name}' on Travel Companion!"
        message = f"""
Hi {recipient_name},

Great news! {trip_creator} has invited you to join a trip on Travel Companion.

Trip Details:
- Trip Name: {trip_name}
- Trip ID: {trip_id}

To view and respond to this invitation:
1. Log in to your Travel Companion account
2. Go to "My Trips" section
3. Find the pending invitation and accept or decline

Can't wait to travel with you!

Best regards,
Travel Companion Team
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient_email],
            fail_silently=False,
        )
    
    @staticmethod
    def send_expense_notification(recipient_email, recipient_name, creator_name, amount, trip_name):
        """Send expense added notification email"""
        subject = f"New expense added to '{trip_name}'"
        message = f"""
Hi {recipient_name},

{creator_name} has added a new expense to your trip "{trip_name}".

Expense Amount: Rs. {amount}

Please log in to view the full expense details and see how costs are being split among participants.

Keep track of expenses: Log in to Travel Companion

Best regards,
Travel Companion Team
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient_email],
            fail_silently=False,
        )
    
    @staticmethod
    def send_match_notification(recipient_email, recipient_name, matched_user_name, similarity_score):
        """Send travel buddy match notification"""
        subject = f"New Travel Buddy Match! 🤝 {matched_user_name}"
        message = f"""
Hi {recipient_name},

Great news! Our matching algorithm found a potential travel buddy for you!

Matched User: {matched_user_name}
Match Compatibility Score: {similarity_score:.0%}

This indicates you have compatible travel preferences and style.

To learn more about {matched_user_name}:
1. Log in to Travel Companion
2. Go to "Find Travel Buddies"
3. Review the match and accept or decline

Start your adventure together!

Best regards,
Travel Companion Team
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient_email],
            fail_silently=False,
        )
    
    @staticmethod
    def send_expense_reminder(recipient_email, recipient_name, trip_name, amount_owed, debtor_name):
        """Send expense settlement reminder"""
        subject = f"Expense Reminder: You owe Rs. {amount_owed} for '{trip_name}'"
        message = f"""
Hi {recipient_name},

This is a friendly reminder that you have an outstanding expense from your trip "{trip_name}".

You owe {debtor_name}: Rs. {amount_owed}

Please settle this expense as soon as possible to keep things fair with your travel buddies.

For payment or more details, log in to Travel Companion.

Thanks for being a responsible travel buddy!

Best regards,
Travel Companion Team
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient_email],
            fail_silently=False,
        )
    
    @staticmethod
    def send_kyc_submission_confirmation(user_email, username):
        """Send KYC document submission confirmation"""
        subject = "KYC Documents Received - Travel Companion"
        message = f"""
Hi {username},

Thank you for submitting your KYC documents!

We have received your submission and our verification team is reviewing it.

What happens next:
1. Our team will verify your documents (usually within 2-3 business days)
2. You'll receive an email once verification is complete
3. Once approved, you'll be able to access all premium features

We appreciate your cooperation in keeping our community safe!

Best regards,
Travel Companion Team
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user_email],
            fail_silently=False,
        )
    
    @staticmethod
    def send_kyc_approval_notification(user_email, username):
        """Send KYC approval notification"""
        subject = "KYC Verification Complete! ✅ - Travel Companion"
        message = f"""
Hi {username},

Great news! Your KYC verification has been approved.

You can now enjoy all features of Travel Companion:
- Create and join trips
- Connect with travel buddies
- Make and receive payments
- And much more!

Welcome to the Travel Companion community!

Best regards,
Travel Companion Team
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user_email],
            fail_silently=False,
        )
    
    @staticmethod
    def send_kyc_rejection_notification(user_email, username, reason):
        """Send KYC rejection notification with reason"""
        subject = "KYC Verification - Action Required - Travel Companion"
        message = f"""
Hi {username},

Your KYC verification could not be approved at this time.

Reason: {reason}

What you can do:
1. Review the rejection reason carefully
2. Update your documents if necessary
3. Resubmit your KYC for verification

If you have questions, please contact our support team.

We're here to help!

Best regards,
Travel Companion Team
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user_email],
            fail_silently=False,
        )
