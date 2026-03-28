from django.db import models
from django.contrib.auth.models import User



class UserProfile(models.Model):

    STATUS_CHOICES = [
        ('pending',  'Pending Verification'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Verification
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    rejection_reason = models.TextField(blank=True, default='')

    # Basic info
    bio      = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    preferred_destinations = models.CharField(max_length=255, blank=True)

    # Travel preferences
    travel_style = models.CharField(
        max_length=50,
        choices=[('budget', 'Budget'), ('luxury', 'Luxury'), ('adventure', 'Adventure')],
        blank=True
    )
    pace = models.CharField(
        max_length=50,
        choices=[('relaxed', 'Relaxed'), ('moderate', 'Moderate'), ('fast_paced', 'Fast-paced')],
        blank=True
    )
    accomodation_preference = models.CharField(
        max_length=50,
        choices=[('hostel', 'Hostel'), ('hotel', 'Hotel'), ('inn', 'Inn'), ('camping', 'Camping')],
        blank=True
    )

    profile_picture = models.ImageField(upload_to='profiles/', blank=True)
    passport_photo  = models.ImageField(upload_to='passports/', blank=True)

    # Extra registration fields (for admin review)
    phone        = models.CharField(max_length=20, blank=True)
    address      = models.CharField(max_length=255, blank=True)
    city         = models.CharField(max_length=100, blank=True)
    country      = models.CharField(max_length=100, blank=True)
    zip_code     = models.CharField(max_length=20, blank=True)
    dob          = models.DateField(null=True, blank=True)
    gender       = models.CharField(max_length=30, blank=True)
    citizenship  = models.CharField(max_length=100, blank=True)
    passport_no  = models.CharField(max_length=50, blank=True)
    passport_expiry = models.DateField(null=True, blank=True)

    # Scores
    budget_level    = models.IntegerField(default=5)
    adventure_level = models.IntegerField(default=5)
    social_level    = models.IntegerField(default=5)

    preference_vector = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} [{self.status}]"


class Match(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="initiated_matches")
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_matches")
    similarity_score = models.FloatField()
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')],
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user1} ↔ {self.user2}"


class UserLoginHistory(models.Model):
    user       = models.ForeignKey(User, on_delete=models.CASCADE)
    login_time = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} logged in at {self.login_time}"


