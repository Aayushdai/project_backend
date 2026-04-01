from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from .models import KYCProfile


# Disabled: Don't auto-create empty KYC profiles
# KYC profiles are only created when users actually submit the form
# @receiver(post_save, sender=get_user_model())
# def create_kyc_profile(sender, instance, created, **kwargs):
#     if created:
#         KYCProfile.objects.create(user=instance)