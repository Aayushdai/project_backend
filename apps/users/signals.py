from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import UserProfile
from core.email_service import EmailService


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):

    if created:
        UserProfile.objects.create(user=instance)
        # Send registration confirmation email
        try:
            EmailService.send_registration_confirmation(
                user_email=instance.email,
                username=instance.username
            )
        except Exception as e:
            print(f"Error sending registration email: {e}")


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()