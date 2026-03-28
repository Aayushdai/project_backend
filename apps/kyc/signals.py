from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from .models import KYCProfile


@receiver(post_save, sender=get_user_model())
def create_kyc_profile(sender, instance, created, **kwargs):
    if created:
        KYCProfile.objects.create(user=instance)