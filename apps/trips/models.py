from django.db import models
from apps.users.models import UserProfile
from django.core.exceptions import ValidationError


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

    def __str__(self):
        return self.name


class Trip(models.Model):
    title = models.CharField(max_length=200)
    destination = models.ForeignKey(City, on_delete=models.CASCADE, related_name='trips')
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.TextField()
    creator = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='created_trips')
    participants = models.ManyToManyField(UserProfile, related_name='joined_trips', blank=True)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def clean(self):
        super().clean()
        if self.end_date < self.start_date:
            raise ValidationError("End date cannot be before start date.")


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