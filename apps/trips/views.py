from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import generics, permissions
from rest_framework.response import Response
from django.contrib.auth.decorators import login_required
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import ListAPIView
from django.db.models import Q, Count, Case, When, IntegerField, F
from .models import Trip, Destination, City, TripExpenseBudget, TripReview, TripInvitation, TripInviteLink, Notification
from .forms import TripForm
from .serializers import TripSerializer, DestinationSerializer, CitySerializer, TripExpenseBudgetSerializer, TripReviewSerializer, TripInvitationSerializer, TripInviteLinkSerializer, NotificationSerializer
from django.http import JsonResponse
from datetime import date, datetime
from apps.kyc.permissions import IsKYCApproved
import logging
import uuid

logger = logging.getLogger(__name__)


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

    def list(self, request, *args, **kwargs):
        """Override list to mark past trips as completed"""
        from datetime import date
        # Mark all past incomplete trips as completed
        today = date.today()
        Trip.objects.filter(end_date__lt=today, is_completed=False).update(is_completed=True)
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        user_profile = self.request.user.userprofile
        today = date.today()
        
        # Get all future public trips (same for all users)
        # PLUS trips where user is creator or participant (to see their own trips)
        queryset = Trip.objects.filter(
            Q(end_date__gte=today, is_public=True) |  # Future public trips visible to everyone
            Q(creator=user_profile) |                  # User's own trips (regardless of date or privacy)
            Q(participants=user_profile)               # User's joined trips (regardless of date)
        ).distinct().order_by('-start_date')
        
        return queryset

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
        # Mark them as completed if not already marked
        trips = Trip.objects.filter(
            Q(creator=user_profile) | Q(participants=user_profile),
            end_date__lt=today
        ).distinct().order_by('-end_date')
        
        # Ensure all past trips are marked as completed
        for trip in trips:
            if not trip.is_completed:
                trip.mark_as_completed()
        
        return trips


class CityListAPIView(generics.ListAPIView):
    queryset = City.objects.all()
    serializer_class = CitySerializer


class DestinationListAPIView(ListAPIView):
    queryset = Destination.objects.select_related('city')
    serializer_class = DestinationSerializer


class TripExpenseBudgetListAPIView(generics.ListCreateAPIView):
    """List and create expense budgets for a trip"""
    serializer_class = TripExpenseBudgetSerializer
    permission_classes = [permissions.IsAuthenticated, IsKYCApproved]

    def get_queryset(self):
        trip_id = self.kwargs.get('trip_id')
        if trip_id:
            return TripExpenseBudget.objects.filter(trip_id=trip_id)
        return TripExpenseBudget.objects.none()

    def perform_create(self, serializer):
        trip_id = self.kwargs.get('trip_id')
        logger.info(f"Attempting to create expense for trip_id={trip_id}")
        logger.info(f"Current user: {self.request.user.userprofile}")
        
        try:
            trip = Trip.objects.get(id=trip_id)
            logger.info(f"Found trip: {trip.title}, creator: {trip.creator}")
            
            # Only creator can add expenses
            if trip.creator != self.request.user.userprofile:
                logger.warning(f"User {self.request.user.userprofile} is not the creator of trip {trip_id}")
                raise PermissionDenied("Only the trip creator can add expenses.")
            
            logger.info(f"User has permission, saving expense: {serializer.validated_data}")
            serializer.save(trip=trip)
            logger.info(f"✅ Expense saved successfully")
        except Trip.DoesNotExist:
            logger.error(f"Trip {trip_id} not found")
            raise PermissionDenied("Trip not found.")


class TripExpenseBudgetDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete an expense budget"""
    serializer_class = TripExpenseBudgetSerializer
    permission_classes = [permissions.IsAuthenticated, IsKYCApproved]
    queryset = TripExpenseBudget.objects.all()

    def get_object(self):
        expense = super().get_object()
        # Only creator of the trip can modify its expenses
        if expense.trip.creator != self.request.user.userprofile:
            raise PermissionDenied("Only the trip creator can modify expenses.")
        return expense


class DestinationDetailAPIView(generics.RetrieveAPIView):
    queryset = Destination.objects.select_related('city')
    serializer_class = DestinationSerializer
    lookup_field = 'id'


def get_destinations(request):
    destinations = list(Destination.objects.values())
    return JsonResponse(destinations, safe=False)


class TripReviewListCreateAPIView(generics.ListCreateAPIView):
    """API view for creating and retrieving reviews for a trip"""
    serializer_class = TripReviewSerializer
    permission_classes = [permissions.IsAuthenticated, IsKYCApproved]
    
    def get_queryset(self):
        """Get all reviews for the specified trip"""
        trip_id = self.kwargs.get('trip_id')
        return TripReview.objects.filter(trip_id=trip_id)
    
    def perform_create(self, serializer):
        """Create a review, ensuring user is a participant of the trip"""
        trip_id = self.kwargs.get('trip_id')
        trip = get_object_or_404(Trip, id=trip_id)
        user_profile = self.request.user.userprofile
        
        # Check if trip is completed
        if trip.end_date >= date.today():
            raise PermissionDenied("Can only review completed trips.")
        
        # Check if user is a participant or creator
        is_participant = user_profile in trip.participants.all() or trip.creator == user_profile
        if not is_participant:
            raise PermissionDenied("Only trip participants can leave reviews.")
        
        # Save the review with the current user as reviewer
        serializer.save(trip=trip, reviewer=user_profile)


class JoinTripByInviteCodeAPIView(generics.GenericAPIView):
    """API view to join a private trip using an invite code"""
    permission_classes = [permissions.IsAuthenticated, IsKYCApproved]
    serializer_class = TripSerializer
    
    def post(self, request, invite_code):
        """Join a trip using invite code"""
        try:
            trip = Trip.objects.get(invite_code=invite_code)
        except Trip.DoesNotExist:
            return Response(
                {"error": "Invalid invite code. Trip not found."},
                status=404
            )
        
        # Check if trip is still open (not completed)
        if trip.is_completed:
            return Response(
                {"error": "This trip has already been completed."},
                status=400
            )
        
        user_profile = request.user.userprofile
        
        # Check if already a participant
        if trip.participants.filter(id=user_profile.id).exists():
            return Response(
                {"message": "You are already a participant of this trip."},
                status=200,
                data=TripSerializer(trip).data
            )
        
        # Add user as participant
        trip.participants.add(user_profile)
        
        return Response(
            {
                "message": f"Successfully joined trip: {trip.title}",
                "trip": TripSerializer(trip).data
            },
            status=200
        )


class GenerateInviteLinkAPIView(generics.CreateAPIView):
    """Generate a shareable invite link for a trip"""
    serializer_class = TripInviteLinkSerializer
    permission_classes = [permissions.IsAuthenticated, IsKYCApproved]
    
    def create(self, request, *args, **kwargs):
        trip_id = self.kwargs.get('trip_id')
        trip = get_object_or_404(Trip, id=trip_id)
        
        # Only trip creator can generate links
        if trip.creator != request.user.userprofile:
            raise PermissionDenied("Only the trip creator can generate invite links.")
        
        # Generate unique code
        code = str(uuid.uuid4())[:8].upper()
        while TripInviteLink.objects.filter(code=code).exists():
            code = str(uuid.uuid4())[:8].upper()
        
        # Create invite link
        invite_link = TripInviteLink.objects.create(
            trip=trip,
            created_by=request.user.userprofile,
            code=code
        )
        
        # Return the response with the invite link
        frontend_url = request.build_absolute_uri('/').rstrip('/')
        return Response({
            'link': f"{frontend_url}/invite/{code}",
            'code': code,
            'trip_id': trip.id
        }, status=201)


class TripInvitationListAPIView(generics.ListCreateAPIView):
    """List all invitations for a trip (GET) and create new invitations (POST)"""
    serializer_class = TripInvitationSerializer
    permission_classes = [permissions.IsAuthenticated, IsKYCApproved]
    
    def get_queryset(self):
        trip_id = self.kwargs.get('trip_id')
        trip = get_object_or_404(Trip, id=trip_id)
        
        # Only creator can view invitations
        if trip.creator != self.request.user.userprofile:
            raise PermissionDenied("Only the trip creator can view invitations.")
        
        return TripInvitation.objects.filter(trip_id=trip_id)
    
    def perform_create(self, serializer):
        trip_id = self.kwargs.get('trip_id')
        trip = get_object_or_404(Trip, id=trip_id)
        
        # Only trip creator can send invitations
        if trip.creator != self.request.user.userprofile:
            raise PermissionDenied("Only the trip creator can send invitations.")
        
        serializer.save(trip=trip, invited_by=self.request.user.userprofile)


class TripInvitationDeleteAPIView(generics.DestroyAPIView):
    """Revoke a pending invitation"""
    serializer_class = TripInvitationSerializer
    permission_classes = [permissions.IsAuthenticated, IsKYCApproved]
    queryset = TripInvitation.objects.all()
    lookup_field = 'pk'
    
    def get_object(self):
        invitation = super().get_object()
        trip = invitation.trip
        
        # Only trip creator can revoke invitations
        if trip.creator != self.request.user.userprofile:
            raise PermissionDenied("Only the trip creator can revoke invitations.")
        
        # Can only revoke pending invitations
        if invitation.status != 'pending':
            raise PermissionDenied("Can only revoke pending invitations.")
        
        return invitation


class MyInvitationsListAPIView(generics.ListAPIView):
    """Get all invitations received by the current user"""
    serializer_class = TripInvitationSerializer
    permission_classes = [permissions.IsAuthenticated, IsKYCApproved]
    
    def get_queryset(self):
        """Get all invitations for current user (pending, accepted, rejected)"""
        user_profile = self.request.user.userprofile
        return TripInvitation.objects.filter(invited_user=user_profile).order_by('-created_at')


class RespondToInvitationAPIView(generics.UpdateAPIView):
    """Accept or reject a trip invitation"""
    serializer_class = TripInvitationSerializer
    permission_classes = [permissions.IsAuthenticated, IsKYCApproved]
    queryset = TripInvitation.objects.all()
    
    def patch(self, request, *args, **kwargs):
        """Accept or reject an invitation"""
        invitation = self.get_object()
        
        # Only the invited user can respond
        if invitation.invited_user != request.user.userprofile:
            raise PermissionDenied("Only the invited user can respond to this invitation.")
        
        # Can only respond to pending invitations
        if invitation.status != 'pending':
            raise PermissionDenied(f"Can only respond to pending invitations. This is {invitation.status}.")
        
        # Check if invitation has expired
        if invitation.is_expired:
            raise PermissionDenied("This invitation has expired (was valid for 1 hour).")
        
        action = request.data.get('action')
        
        if action == 'accept':
            invitation.status = 'accepted'
            invitation.accepted_at = datetime.now()
            # Add user as participant to the trip
            invitation.trip.participants.add(invitation.invited_user)
            invitation.save()
            return Response({
                'message': f'Successfully joined trip: {invitation.trip.title}',
                'status': 'accepted',
                'trip': TripSerializer(invitation.trip).data
            })
        elif action == 'reject':
            invitation.status = 'rejected'
            invitation.rejected_at = datetime.now()
            invitation.save()
            return Response({
                'message': 'Invitation declined',
                'status': 'rejected'
            })
        else:
            return Response({
                'error': 'Invalid action. Use "accept" or "reject".'
            }, status=400)


class NotificationListAPIView(generics.ListAPIView):
    """Get all notifications for the current user"""
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated, IsKYCApproved]
    
    def get_queryset(self):
        """Get all notifications for current user, ordered by most recent"""
        user_profile = self.request.user.userprofile
        return Notification.objects.filter(recipient=user_profile).order_by('-created_at')


class UnreadNotificationCountAPIView(generics.RetrieveAPIView):
    """Get count of unread notifications"""
    permission_classes = [permissions.IsAuthenticated, IsKYCApproved]
    
    def retrieve(self, request, *args, **kwargs):
        """Return count of unread notifications"""
        user_profile = request.user.userprofile
        unread_count = Notification.objects.filter(
            recipient=user_profile,
            is_read=False
        ).count()
        return Response({'unread_count': unread_count})


class NotificationMarkAsReadAPIView(generics.UpdateAPIView):
    """Mark a notification as read"""
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated, IsKYCApproved]
    queryset = Notification.objects.all()
    
    def patch(self, request, *args, **kwargs):
        """Mark notification as read"""
        notification = self.get_object()
        
        # Only the recipient can mark as read
        if notification.recipient != request.user.userprofile:
            raise PermissionDenied("You can only mark your own notifications as read.")
        
        notification.is_read = True
        notification.save()
        return Response({
            'message': 'Notification marked as read',
            'notification': NotificationSerializer(notification).data
        })


class NotificationMarkAllAsReadAPIView(generics.UpdateAPIView):
    """Mark all notifications as read"""
    permission_classes = [permissions.IsAuthenticated, IsKYCApproved]
    
    def patch(self, request, *args, **kwargs):
        """Mark all notifications as read for current user"""
        user_profile = request.user.userprofile
        count = Notification.objects.filter(
            recipient=user_profile,
            is_read=False
        ).update(is_read=True)
        return Response({
            'message': f'{count} notifications marked as read',
            'count': count
        })