from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Expense
from apps.trips.models import Trip
from django.contrib import messages
from .forms import ExpenseForm
from rest_framework import generics, permissions
from .serializers import ExpenseSerializer


# --- API View ---
class ExpenseListView(generics.ListAPIView):
    serializer_class = ExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Expense.objects.filter(
            trip__creator=self.request.user.userprofile
        ).order_by('-date')


# --- Template Views ---
@login_required
def add_expense(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id)

    if request.method == 'POST':
        form = ExpenseForm(request.POST)

        if form.is_valid():
            expense = form.save(commit=False)
            expense.trip = trip
            expense.paid_by = request.user.userprofile
            expense.save()
            expense.split_among.set(trip.participants.all())
            messages.success(request, f"Expense of {expense.amount} added!")
            return redirect('trip_detail', trip_id=trip.id)
    else:
        form = ExpenseForm(initial={'paid_by': request.user.userprofile})

    return render(request, 'expenses/add_expense.html', {
        'form': form,
        'trip': trip,
        'title': f"Add expense to {trip.title}",
    })