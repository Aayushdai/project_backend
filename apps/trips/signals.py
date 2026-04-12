from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import TripInvitation, Notification, Trip

@receiver(post_save, sender=TripInvitation)
def create_notification_on_invitation(sender, instance, created, **kwargs):
    """Create notification when user is invited to a trip"""
    if created and instance.status == 'pending':
        Notification.objects.create(
            recipient=instance.invited_user,
            actor=instance.invited_by,
            trip=instance.trip,
            invitation=instance,
            notification_type=Notification.INVITATION_RECEIVED,
            message=f'{instance.invited_by.user.get_full_name() or instance.invited_by.user.username} invited you to {instance.trip.title}'
        )


@receiver(post_save, sender=TripInvitation)
def create_notification_on_invitation_response(sender, instance, created, **kwargs):
    """Create notification when invitation is accepted or rejected"""
    if not created:
        # Get the previous state to detect status change
        try:
            # We need to manually fetch to detect changes
            # Use a helper to track old vs new status
            pass
        except Exception:
            pass
        
        # Check if this invitation has a pending notification we should delete
        if instance.status == 'accepted':
            # Delete the pending invitation_received notification
            Notification.objects.filter(
                recipient=instance.invited_user,
                trip=instance.trip,
                notification_type=Notification.INVITATION_RECEIVED,
                invitation=instance
            ).delete()
            
            # Create acceptance notification for the inviter
            Notification.objects.create(
                recipient=instance.invited_by,
                actor=instance.invited_user,
                trip=instance.trip,
                invitation=instance,
                notification_type=Notification.INVITATION_ACCEPTED,
                message=f'{instance.invited_user.user.get_full_name() or instance.invited_user.user.username} accepted your invitation to {instance.trip.title}'
            )
        elif instance.status == 'rejected':
            # Delete the pending invitation_received notification
            Notification.objects.filter(
                recipient=instance.invited_user,
                trip=instance.trip,
                notification_type=Notification.INVITATION_RECEIVED,
                invitation=instance
            ).delete()
            
            # Create rejection notification for the inviter
            Notification.objects.create(
                recipient=instance.invited_by,
                actor=instance.invited_user,
                trip=instance.trip,
                invitation=instance,
                notification_type=Notification.INVITATION_REJECTED,
                message=f'{instance.invited_user.user.get_full_name() or instance.invited_user.user.username} declined your invitation to {instance.trip.title}'
            )


