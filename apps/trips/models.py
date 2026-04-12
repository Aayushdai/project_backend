from django.db import models
from apps.users.models import UserProfile, ConstraintTag
from django.core.exceptions import ValidationError
import uuid


class City(models.Model):
    name = models.CharField(max_length=50)
    country = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name}, {self.country}"


class Destination(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    location = models.CharField(max_length=100)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='destinations')
    image = models.ImageField(upload_to='destinations/', null=True, blank=True)

    def __str__(self):
        return self.name


class Trip(models.Model):
    title = models.CharField(max_length=200)
    destination = models.ForeignKey(City, on_delete=models.CASCADE, related_name='trips')
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.TextField()
    cover_image = models.ImageField(upload_to='trips/', null=True, blank=True)
    creator = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='created_trips')
    participants = models.ManyToManyField(UserProfile, related_name='joined_trips', blank=True)
    constraint_tags = models.ManyToManyField(ConstraintTag, related_name='trips', blank=True)
    trip_tags = models.JSONField(default=list, blank=True)  # Stores selected tags as list of strings
    is_public = models.BooleanField(default=True)
    is_completed = models.BooleanField(default=False)  # Tracks if trip has been completed
    invite_code = models.CharField(max_length=12, unique=True, null=True, blank=True)  # Shareable code for private trips
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """Generate invite code for private trips"""
        if not self.is_public and not self.invite_code:
            self.invite_code = self.generate_invite_code()
        elif self.is_public and self.invite_code:
            # Clear invite code if trip becomes public
            self.invite_code = None
        super().save(*args, **kwargs)
    
    @staticmethod
    def generate_invite_code():
        """Generate a unique invite code for private trips"""
        # Generate a short unique code using UUID
        code = str(uuid.uuid4())[:8].upper()
        while Trip.objects.filter(invite_code=code).exists():
            code = str(uuid.uuid4())[:8].upper()
        return code

    def clean(self):
        super().clean()
        from datetime import date
        today = date.today()
        
        # Cannot create trips in the past (no time traveling!)
        if self.start_date < today:
            raise ValidationError("Trip start date cannot be before today.")
        
        if self.end_date < self.start_date:
            raise ValidationError("End date cannot be before start date.")
    
    @property
    def is_trip_ended(self):
        """Check if trip end date has passed"""
        from datetime import date
        return self.end_date < date.today()
    
    def mark_as_completed(self):
        """Mark the trip as completed"""
        if self.is_trip_ended and not self.is_completed:
            self.is_completed = True
            self.save(update_fields=['is_completed', 'updated_at'])
    
    @property
    def total_expense(self):
        """Calculate total expense amount from all budget categories"""
        return sum(expense.amount for expense in self.expense_budgets.all())


class ItineraryItem(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='itinerary')
    day = models.IntegerField()
    activity = models.CharField(max_length=200)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ('trip', 'day')
        ordering = ['day']

    def __str__(self):
        return f"{self.trip.title} - Day{self.day}"


class TripExpenseBudget(models.Model):
    """Stores trip budget categories and their estimated costs"""
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='expense_budgets')
    category = models.CharField(max_length=100)  # e.g., "Bus", "Room", "Food", "Activities"
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.trip.title} - {self.category}: ${self.amount}"


class TripReview(models.Model):
    """Stores reviews from trip participants after trip completion"""
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='trip_reviews')
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], default=5)  # 1-5 stars
    text = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('trip', 'reviewer')  # One review per participant per trip

    def __str__(self):
        return f"Review of {self.trip.title} by {self.reviewer.first_name}"


class TripInvitation(models.Model):
    """Stores invitations sent to users for joining trips"""
    PENDING = 'pending'
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'
    
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (ACCEPTED, 'Accepted'),
        (REJECTED, 'Rejected'),
    ]
    
    ROLE_CHOICES = [
        ('member', 'Member'),
        ('organizer', 'Organizer'),
    ]
    
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='invitations')
    invited_user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='invitations_received')
    invited_by = models.ForeignKey(UserProfile, on_delete=models.PROTECT, related_name='invitations_sent')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    rejected_at = models.DateTimeField(null=True, blank=True)
    def save(self, *args, **kwargs):
        """Set expiration time to 1 hour from creation if not already set"""
        from django.utils import timezone
        from datetime import timedelta
        
        if not self.expires_at and not self.pk:
            self.expires_at = timezone.now() + timedelta(hours=1)
        super().save(*args, **kwargs)
    
    @property
    def is_expired(self):
        """Check if invitation has expired"""
        from django.utils import timezone
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    def __str__(self):
        return f"Invitation for {self.invited_user.user.username} to {self.trip.title}"


class TripInviteLink(models.Model):
    """Stores shareable invite links for trips"""
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='invite_links')
    created_by = models.ForeignKey(UserProfile, on_delete=models.PROTECT)
    code = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Invite link for {self.trip.title}"


class Notification(models.Model):
    """Stores trip-related notifications for users"""
    INVITATION_RECEIVED = 'invitation_received'
    INVITATION_ACCEPTED = 'invitation_accepted'
    INVITATION_REJECTED = 'invitation_rejected'
    MEMBER_JOINED = 'member_joined'
    MEMBER_LEFT = 'member_left'
    TRIP_UPDATED = 'trip_updated'
    
    NOTIFICATION_TYPE_CHOICES = [
        (INVITATION_RECEIVED, 'Invitation Received'),
        (INVITATION_ACCEPTED, 'Invitation Accepted'),
        (INVITATION_REJECTED, 'Invitation Rejected'),
        (MEMBER_JOINED, 'Member Joined'),
        (MEMBER_LEFT, 'Member Left'),
        (TRIP_UPDATED, 'Trip Updated'),
    ]
    
    recipient = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='notifications_received')
    actor = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='notifications_sent')
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='notifications')
    invitation = models.ForeignKey(TripInvitation, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPE_CHOICES)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"[{self.get_notification_type_display()}] {self.recipient.user.username}"