"""
Email notification helpers for Trip-related events
"""

from core.email_service import EmailService


def notify_trip_invitation(participant, trip):
    """
    Send email notification when a user is invited to a trip
    
    Args:
        participant: UserProfile instance of the invited participant
        trip: Trip instance
    """
    try:
        if participant.user.email:
            EmailService.send_trip_invitation(
                recipient_email=participant.user.email,
                recipient_name=participant.user.first_name or participant.user.username,
                trip_creator=trip.creator.user.get_full_name() or trip.creator.user.username,
                trip_name=trip.title,
                trip_id=trip.id
            )
    except Exception as e:
        print(f"Error sending trip invitation email for {participant.user.email}: {e}")


def notify_trip_participants_expense(expense):
    """
    Send email notification to all trip participants when an expense is added
    
    Args:
        expense: Expense instance
    """
    trip = expense.trip
    creator_name = expense.paid_by.user.get_full_name() or expense.paid_by.user.username
    
    for participant in trip.participants.all():
        # Don't send email to the one who created the expense
        if participant != expense.paid_by:
            try:
                if participant.user.email:
                    EmailService.send_expense_notification(
                        recipient_email=participant.user.email,
                        recipient_name=participant.user.first_name or participant.user.username,
                        creator_name=creator_name,
                        amount=expense.amount,
                        trip_name=trip.title
                    )
            except Exception as e:
                print(f"Error sending expense notification to {participant.user.email}: {e}")
