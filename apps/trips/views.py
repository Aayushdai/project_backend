from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import generics, permissions
from django.contrib.auth.decorators import login_required
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import ListAPIView
from django.db.models import Q
from .models import Trip, Destination, City
from .forms import TripForm
from .serializers import TripSerializer, DestinationSerializer, CitySerializer
from django.http import JsonResponse


@login_required
def create_trip(request):
    if request.method == 'POST':
        form = TripForm(request.POST)
        if form.is_valid():
            trip = form.save(commit=False)
            trip.creator = request.user.userprofile
            trip.save()
            trip.participants.add(trip.creator)
            return redirect('trip_detail', trip_id=trip.id)
    else:
        form = TripForm()
    return render(request, 'trips/create.html', {'form': form})


@login_required
def trip_detail(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id)
    if not trip.is_public and request.user.userprofile != trip.creator:
        return redirect('home')
    return render(request, 'trips/details.html', {'trip': trip})


class TripListAPIView(generics.ListCreateAPIView):
    serializer_class = TripSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_profile = self.request.user.userprofile
        return Trip.objects.filter(
            Q(is_public=True) | Q(creator=user_profile)
        ).order_by('-start_date')

    def perform_create(self, serializer):
        trip = serializer.save(creator=self.request.user.userprofile)
        trip.participants.add(trip.creator)


class TripDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TripSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Trip.objects.all()

    def get_object(self):
        trip = super().get_object()
        if self.request.method not in ('GET', 'HEAD', 'OPTIONS'):
            if trip.creator != self.request.user.userprofile:
                raise PermissionDenied("You do not have permission to modify this trip.")
        return trip


class CityListAPIView(generics.ListAPIView):
    queryset = City.objects.all()
    serializer_class = CitySerializer


class DestinationListAPIView(ListAPIView):
    queryset = Destination.objects.select_related('city')
    serializer_class = DestinationSerializer


def get_destinations(request):
    destinations = list(Destination.objects.values())
    return JsonResponse(destinations, safe=False)