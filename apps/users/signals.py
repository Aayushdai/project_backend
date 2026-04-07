from django.db.models.signals import post_save
from django.db.models.signals import post_migrate
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import UserProfile, SecurityQuestion
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


@receiver(post_migrate)
def populate_security_questions(sender, app_config, **kwargs):
    """Populate SecurityQuestion table with initial questions after migrations"""
    if app_config.name != 'apps.users':
        return
    
    # Only populate if table is empty
    if SecurityQuestion.objects.exists():
        return
    
    initial_questions = [
        # Personal category
        ("What was the name of your first pet?", "personal"),
        ("What is your mother's maiden name?", "personal"),
        ("In what city were you born?", "personal"),
        ("What is your favorite book?", "personal"),
        ("What is your all-time favorite movie?", "personal"),
        ("What is the name of the street you grew up on?", "personal"),
        ("What is your favorite food?", "personal"),
        
        # Pet category
        ("What was the name of your first dog?", "pet"),
        ("What was the name of your first cat?", "pet"),
        ("What was your favorite childhood pet?", "pet"),
        
        # Food category
        ("What is your favorite cuisine?", "food"),
        ("What is your favorite restaurant?", "food"),
        ("What is your favorite dessert?", "food"),
        
        # Travel category
        ("What is your favorite country to visit?", "travel"),
        ("What is your dream vacation destination?", "travel"),
        ("What is the best place you have traveled to?", "travel"),
        ("What is your favorite beach?", "travel"),
        
        # Other category
        ("What is your favorite hobby?", "other"),
        ("What is your favorite color?", "other"),
        ("What is your favorite season?", "other"),
        ("What is your favorite sport?", "other"),
    ]
    
    for question_text, category in initial_questions:
        SecurityQuestion.objects.get_or_create(
            question=question_text,
            defaults={'category': category}
        )