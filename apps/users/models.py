from django.db import models
from django.contrib.auth.models import User


class Interest(models.Model):
    """Travel interests/tags for cosine similarity matching (soft matching)"""
    CATEGORY_CHOICES = [
        ('activity', 'Activity'),
        ('destination', 'Destination'),
        ('experience', 'Experience'),
    ]
    
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='activity')
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['category', 'name']


class ConstraintTag(models.Model):
    """Strict matching tags (lifestyle, diet, age range, values)"""
    CATEGORY_CHOICES = [
        ('diet', 'Diet'),
        ('lifestyle', 'Lifestyle'),
        ('values', 'Values'),
        ('age_range', 'Age Range'),
    ]
    
    name = models.CharField(max_length=50)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.get_category_display()}: {self.name}"
    
    class Meta:
        unique_together = ('category', 'name')
        ordering = ['category', 'name']


class UserProfile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)

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

    # ✅ Interests (soft matching - for cosine similarity)
    interests = models.ManyToManyField(Interest, related_name='users', blank=True)

    # ✅ Constraint Tags (strict matching - must align for good match)
    constraint_tags = models.ManyToManyField(ConstraintTag, related_name='users', blank=True, 
                                            help_text="Diet, lifestyle, values - these must match for compatibility")
    
    # Age preferences for matching
    min_match_age = models.IntegerField(default=18, help_text="Minimum age for travel companions")
    max_match_age = models.IntegerField(default=100, help_text="Maximum age for travel companions")

    # ✅ Privacy Preferences
    public_profile = models.BooleanField(default=True, help_text="Allow others to see your profile")
    searchable_by_email = models.BooleanField(default=True, help_text="Allow users to find you by email")
    show_online_status = models.BooleanField(default=True, help_text="Show when you're online")
    share_trip_activity = models.BooleanField(default=True, help_text="Share your trip activity with others")
    
    # ✅ Online Status
    is_online = models.BooleanField(default=False, help_text="User's current online status")

    # ✅ Notification Preferences
    email_notifications = models.BooleanField(default=True, help_text="Receive email notifications")
    trip_updates = models.BooleanField(default=True, help_text="Get notified about trip updates")
    friend_requests = models.BooleanField(default=True, help_text="Get notified about friend requests")

    preference_vector = models.JSONField(null=True, blank=True)

    def __str__(self):
        # Get KYC status from related KYCProfile if it exists
        kyc_status = "Not Started"
        if hasattr(self.user, 'kyc_profile'):
            kyc_status = self.user.kyc_profile.get_status_display() or self.user.kyc_profile.status
        return f"{self.user.username} [KYC: {kyc_status}]"


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


# ✅ Security Questions for Password Recovery
class SecurityQuestion(models.Model):
    """Predefined security questions for password recovery"""
    question = models.CharField(max_length=255, unique=True)
    category = models.CharField(
        max_length=50,
        choices=[('personal', 'Personal'), ('pet', 'Pet'), ('food', 'Food'), ('travel', 'Travel'), ('other', 'Other')],
        default='personal'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question

    class Meta:
        ordering = ['category', 'question']


class UserSecurityAnswer(models.Model):
    """User's answers to security questions (for password recovery)"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='security_answers')
    
    # Store 2-3 question-answer pairs as JSON for flexibility
    questions_answers = models.JSONField(
        default=dict,
        help_text="Stores question_id: answer_hash pairs"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Security answers for {self.user.username}"


class FriendRequest(models.Model):
    """Friend request between two users"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friend_requests_sent')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friend_requests_received')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('from_user', 'to_user')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.from_user.username} → {self.to_user.username} ({self.status})"


