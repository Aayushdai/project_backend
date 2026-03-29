"""
Email notification helpers for User-related events (matches, KYC, etc.)
"""

from core.email_service import EmailService


def notify_new_match(match_user_profile, matched_user_name, similarity_score):
    """
    Send email notification for a new travel buddy match
    
    Args:
        match_user_profile: UserProfile of the user receiving the match
        matched_user_name: Name of the matched user
        similarity_score: Similarity score as float (0-1)
    """
    try:
        if match_user_profile.user.email:
            EmailService.send_match_notification(
                recipient_email=match_user_profile.user.email,
                recipient_name=match_user_profile.user.first_name or match_user_profile.user.username,
                matched_user_name=matched_user_name,
                similarity_score=similarity_score
            )
    except Exception as e:
        print(f"Error sending match notification email to {match_user_profile.user.email}: {e}")


def notify_kyc_submission_confirmation(user):
    """
    Send confirmation email when KYC documents are submitted
    
    Args:
        user: Django User instance
    """
    try:
        if user.email:
            EmailService.send_kyc_submission_confirmation(
                user_email=user.email,
                username=user.first_name or user.username
            )
    except Exception as e:
        print(f"Error sending KYC submission confirmation email to {user.email}: {e}")


def notify_kyc_approved(user):
    """
    Send notification when KYC is approved
    
    Args:
        user: Django User instance
    """
    try:
        if user.email:
            EmailService.send_kyc_approval_notification(
                user_email=user.email,
                username=user.first_name or user.username
            )
    except Exception as e:
        print(f"Error sending KYC approval email to {user.email}: {e}")


def notify_kyc_rejected(user, rejection_reason):
    """
    Send notification when KYC is rejected with reason
    
    Args:
        user: Django User instance
        rejection_reason: Reason for rejection
    """
    try:
        if user.email:
            EmailService.send_kyc_rejection_notification(
                user_email=user.email,
                username=user.first_name or user.username,
                reason=rejection_reason
            )
    except Exception as e:
        print(f"Error sending KYC rejection email to {user.email}: {e}")
