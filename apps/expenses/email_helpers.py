"""
Email notification helpers for Expense-related events
"""

from core.email_service import EmailService


def notify_settlement_reminder(debtor_userprofile, creditor_name, amount, trip_name):
    """
    Send email reminder to user about pending expense settlement
    
    Args:
        debtor_userprofile: UserProfile of the person who owes money
        creditor_name: Name of the person who paid
        amount: Amount owed
        trip_name: Name of the trip
    """
    try:
        if debtor_userprofile.user.email:
            EmailService.send_expense_reminder(
                recipient_email=debtor_userprofile.user.email,
                recipient_name=debtor_userprofile.user.first_name or debtor_userprofile.user.username,
                trip_name=trip_name,
                amount_owed=amount,
                debtor_name=creditor_name
            )
    except Exception as e:
        print(f"Error sending expense reminder email to {debtor_userprofile.user.email}: {e}")
