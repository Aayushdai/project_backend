from django.db import models
from apps.trips.models import Trip
from apps.users.models import UserProfile


class Expense(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='expenses')
    description = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_by = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True)
    split_among = models.ManyToManyField(UserProfile, related_name='shared_expenses')
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.description} - {self.amount}"