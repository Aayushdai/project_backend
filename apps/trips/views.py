from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import generics, permissions
from rest_framework.response import Response
from django.contrib.auth.decorators import login_required
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import ListAPIView
from django.db.models import Q, Count, Case, When, IntegerField, F
from .models import Trip, Destination, City
from .forms import TripForm
from .serializers import TripSerializer, DestinationSerializer, CitySerializer
from django.http import JsonResponse
from datetime import date
from apps.kyc.permissions import IsKYCApproved


def kyc_required(view_func):
    """Decorator to check if user has approved KYC status"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        try:
            kyc_profile = request.user.kyc_profile
            if kyc_profile.status != 'approved':
                return redirect('kyc_form')  # Redirect to KYC form if not approved
        except:
            return redirect('kyc_form')  # Redirect to KYC form if no KYC profile
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required
@kyc_required
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
@kyc_required
def trip_detail(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id)
    if not trip.is_public and request.user.userprofile != trip.creator:
        return redirect('home')
    return render(request, 'trips/details.html', {'trip': trip})


class TripListAPIView(generics.ListCreateAPIView):
    serializer_class = TripSerializer
    permission_classes = [permissions.IsAuthenticated, IsKYCApproved]

    def get_queryset(self):
        user_profile = self.request.user.userprofile
        today = date.today()
        
        # Get all future public trips (same for all users)
        # PLUS trips where user is creator or participant (to see their own trips)
        trips = Trip.objects.filter(
            Q(end_date__gte=today, is_public=True) |  # Future public trips visible to everyone
            Q(creator=user_profile) |                  # User's own trips (regardless of date)
            Q(participants=user_profile)               # User's joined trips (regardless of date)
        ).distinct()
        
        # Get user's constraint tags
        user_tags = set(user_profile.constraint_tags.values_list('id', flat=True))
        
        # Sort by similarity: trips with matching tags first, then by date
        def get_similarity_score(trip):
            trip_tags = set(trip.constraint_tags.values_list('id', flat=True))
            if not user_tags and not trip_tags:
                return 0  # Both have no tags
            if not user_tags or not trip_tags:
                return -1000  # One has no tags, lower priority
            # Calculate Jaccard similarity
            intersection = len(user_tags & trip_tags)
            union = len(user_tags | trip_tags)
            return intersection / union if union > 0 else 0
        
        # Sort: first by similarity (descending), then by date (descending)
        trips_list = list(trips)
        trips_list.sort(key=lambda t: (-get_similarity_score(t), -t.start_date.toordinal()))
        
        return trips_list

    def get_queryset_qs(self):
        """Return QuerySet version (used by DRF pagination if needed)"""
        user_profile = self.request.user.userprofile
        return Trip.objects.filter(
            Q(is_public=True) | Q(creator=user_profile) | Q(participants=user_profile)
        ).distinct().order_by('-start_date')

    def perform_create(self, serializer):
        trip = serializer.save(creator=self.request.user.userprofile)
        trip.participants.add(trip.creator)


class TripDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TripSerializer
    permission_classes = [permissions.IsAuthenticated, IsKYCApproved]
    queryset = Trip.objects.all()

    def get_object(self):
        trip = super().get_object()
        if self.request.method not in ('GET', 'HEAD', 'OPTIONS', 'PATCH'):
            if trip.creator != self.request.user.userprofile:
                raise PermissionDenied("You do not have permission to modify this trip.")
        return trip

    def delete(self, request, *args, **kwargs):
        """Delete a trip only if user is creator and no other participants exist"""
        trip = self.get_object()
        user_profile = request.user.userprofile
        
        # Check if user is the creator
        if trip.creator != user_profile:
            raise PermissionDenied("Only the trip creator can delete this trip.")
        
        # Check if there are other participants (besides the creator)
        other_participants = trip.participants.exclude(id=user_profile.id).count()
        if other_participants > 0:
            return Response({
                "message": "Cannot delete trip with other participants. Ask them to leave first."
            }, status=400)
        
        # Safe to delete
        return super().delete(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        trip = self.get_object()
        action = request.data.get('action')
        user_profile = request.user.userprofile
        today = date.today()

        if action == 'join':
            # Check if trip has ended
            if trip.end_date < today:
                return Response({
                    "message": "This trip has already ended. You cannot join completed trips.",
                    "error": "trip_ended"
                }, status=400)
            
            # Check if user is already a participant
            if not trip.participants.filter(id=user_profile.id).exists():
                trip.participants.add(user_profile)
            # Always return the trip with current participants
            return Response({
                "message": "Joined trip successfully",
                "trip": TripSerializer(trip).data
            }, status=200)

        elif action == 'leave':
            # Only allow leaving if you're not the creator
            if user_profile != trip.creator and trip.participants.filter(id=user_profile.id).exists():
                trip.participants.remove(user_profile)
            # Always return the trip with current participants
            return Response({
                "message": "Left trip successfully",
                "trip": TripSerializer(trip).data
            }, status=200)

        # Default update behavior
        return super().patch(request, *args, **kwargs)


class TripHistoryAPIView(generics.ListAPIView):
    """Get completed/past trips for the user"""
    serializer_class = TripSerializer
    permission_classes = [permissions.IsAuthenticated, IsKYCApproved]

    def get_queryset(self):
        user_profile = self.request.user.userprofile
        today = date.today()
        
        # Get only past trips where user is creator or participant
        trips = Trip.objects.filter(
            Q(creator=user_profile) | Q(participants=user_profile),
            end_date__lt=today
        ).distinct().order_by('-end_date')
        
        return trips


class CityListAPIView(generics.ListAPIView):
    queryset = City.objects.all()
    serializer_class = CitySerializer


class DestinationListAPIView(ListAPIView):
    queryset = Destination.objects.select_related('city')
    serializer_class = DestinationSerializer


class DestinationDetailAPIView(generics.RetrieveAPIView):
    queryset = Destination.objects.select_related('city')
    serializer_class = DestinationSerializer
    lookup_field = 'id'


def get_destinations(request):
    destinations = list(Destination.objects.values())
    return JsonResponse(destinations, safe=False)