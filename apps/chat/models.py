from django.db import models
from apps.users.models import UserProfile
from apps.trips.models import Trip

class Message(models.Model):
    sender = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='received_messages', null=True, blank=True)
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_system = models.BooleanField(default=False, help_text="System message (e.g., user joined/left)")
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        if self.trip:
            return f"Group: {self.sender} in {self.trip.title} at {self.timestamp}"
        return f"Direct: {self.sender} to {self.receiver} at {self.timestamp}"


class ChatMessage(models.Model):
    """ChatBot conversation messages"""
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='chat_messages')
    message = models.TextField()
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.user.username} - {self.created_at}"

