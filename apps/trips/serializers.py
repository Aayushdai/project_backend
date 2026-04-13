from rest_framework import serializers
from .models import Trip, City, ItineraryItem, Destination, TripExpenseBudget, TripReview, TripInvitation, TripInviteLink, Notification
from apps.users.models import UserProfile, ConstraintTag
import json


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'name', 'country']


class UserProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'bio', 'first_name', 'last_name', 'username']


class ConstraintTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConstraintTag
        fields = ['id', 'name', 'category']


class ItineraryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItineraryItem
        fields = ['id', 'day', 'activity', 'notes']


class TripExpenseBudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = TripExpenseBudget
        fields = ['id', 'category', 'amount', 'created_at', 'updated_at']


class TripSerializer(serializers.ModelSerializer):
    creator = UserProfileSerializer(read_only=True)
    participants = UserProfileSerializer(many=True, read_only=True)
    itinerary = ItineraryItemSerializer(many=True, read_only=True)
    expense_budgets = TripExpenseBudgetSerializer(many=True, read_only=True)
    destination = CitySerializer(read_only=True)  # Read: nested object
    destination_id = serializers.IntegerField(write_only=True)  # Write: just ID
    constraint_tags = ConstraintTagSerializer(many=True, read_only=True)
    constraint_tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=ConstraintTag.objects.all(),
        write_only=True,
        many=True,
        required=False
    )
    trip_tags = serializers.JSONField(required=False, default=list)
    total_expense = serializers.SerializerMethodField()

    class Meta:
        model = Trip
        fields = [
            'id', 'title', 'destination', 'destination_id', 'start_date', 'end_date',
            'description', 'cover_image', 'creator', 'participants', 'constraint_tags', 'constraint_tag_ids',
            'trip_tags', 'is_public', 'is_completed', 'invite_code', 'created_at', 'updated_at', 'itinerary', 'expense_budgets', 'total_expense'
        ]

    def get_total_expense(self, obj):
        """Calculate and return total expense amount"""
        return obj.total_expense

    def validate(self, data):
        """Validate that end_date is not before start_date"""
        if 'start_date' in data and 'end_date' in data:
            if data['end_date'] < data['start_date']:
                raise serializers.ValidationError({
                    "end_date": "End date cannot be before start date."
                })
        return data

    def create(self, validated_data):
        destination_id = validated_data.pop('destination_id')
        constraint_tag_ids = validated_data.pop('constraint_tag_ids', [])
        trip_tags = validated_data.pop('trip_tags', [])
        
        # Handle trip_tags if it's a JSON string (from FormData)
        if isinstance(trip_tags, str):
            try:
                trip_tags = json.loads(trip_tags)
            except (json.JSONDecodeError, TypeError):
                trip_tags = []
        elif not isinstance(trip_tags, list):
            trip_tags = []
        
        try:
            destination = City.objects.get(id=destination_id)
        except City.DoesNotExist:
            raise serializers.ValidationError({"destination_id": "City not found"})
        
        instance = Trip.objects.create(
            destination=destination,
            trip_tags=trip_tags,
            **validated_data
        )
        
        # Add constraint tags
        for tag_id in constraint_tag_ids:
            instance.constraint_tags.add(tag_id)
        
        return instance

    def update(self, instance, validated_data):
        constraint_tag_ids = validated_data.pop('constraint_tag_ids', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if constraint_tag_ids is not None:
            instance.constraint_tags.clear()
            for tag_id in constraint_tag_ids:
                instance.constraint_tags.add(tag_id)
        
        return instance


class DestinationSerializer(serializers.ModelSerializer):
    city = serializers.StringRelatedField()

    class Meta:
        model = Destination
        fields = '__all__'


class TripReviewSerializer(serializers.ModelSerializer):
    reviewer_name = serializers.CharField(source='reviewer.user.get_full_name', read_only=True)
    
    class Meta:
        model = TripReview
        fields = ['id', 'rating', 'text', 'reviewer_name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'reviewer_name', 'created_at', 'updated_at']


class TripInvitationSerializer(serializers.ModelSerializer):
    """Serializer for trip invitations"""
    invited_user_name = serializers.CharField(source='invited_user.user.get_full_name', read_only=True)
    invited_user_email = serializers.CharField(source='invited_user.user.email', read_only=True)
    invited_by_name = serializers.CharField(source='invited_by.user.get_full_name', read_only=True)
    avatar = serializers.SerializerMethodField()
    email = serializers.CharField(source='invited_user.user.email', read_only=True)  # Alias for pending tab display
    sentAt = serializers.SerializerMethodField()
    is_expired = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = TripInvitation
        fields = [
            'id', 'trip', 'invited_user', 'invited_user_name', 'invited_user_email',
            'invited_by', 'invited_by_name', 'status', 'role', 'avatar', 'email', 'sentAt',
            'created_at', 'expires_at', 'accepted_at', 'rejected_at', 'is_expired'
        ]
        read_only_fields = ['id', 'trip', 'created_at', 'expires_at', 'accepted_at', 'rejected_at', 'invited_by', 'is_expired']
    
    def get_avatar(self, obj):
        """Return user's initials as avatar"""
        user = obj.invited_user.user
        first = user.first_name[0] if user.first_name else ''
        last = user.last_name[0] if user.last_name else ''
        return (first + last).upper() or user.username[0].upper()
    
    def get_sentAt(self, obj):
        """Return formatted creation time"""
        return obj.created_at.strftime('%Y-%m-%d')
    
    def create(self, validated_data):
        """Create invitation and check for duplicates"""
        trip = validated_data.get('trip')
        invited_user = validated_data.get('invited_user')
        
        # Debug logging
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Creating invitation: trip={trip}, invited_user={invited_user}")
        
        if not trip:
            raise serializers.ValidationError({"trip": "Trip is required"})
        if not invited_user:
            raise serializers.ValidationError({"invited_user": "invited_user is required"})
        
        # Check if already invited
        if TripInvitation.objects.filter(trip=trip, invited_user=invited_user).exists():
            raise serializers.ValidationError("User is already invited to this trip")
        
        # Check if already a participant
        if trip.participants.filter(id=invited_user.id).exists():
            raise serializers.ValidationError("User is already a member of this trip")
        
        return super().create(validated_data)


class TripInviteLinkSerializer(serializers.ModelSerializer):
    """Serializer for trip invite links"""
    
    class Meta:
        model = TripInviteLink
        fields = ['id', 'trip', 'code', 'created_at', 'expires_at']
        read_only_fields = ['id', 'code', 'created_at']


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for trip notifications"""
    trip_title = serializers.CharField(source='trip.title', read_only=True)
    trip_destination = serializers.CharField(source='trip.destination.name', read_only=True)
    actor_name = serializers.SerializerMethodField(read_only=True)
    actor_id = serializers.IntegerField(source='actor.id', read_only=True, allow_null=True)
    notification_type_display = serializers.CharField(source='get_notification_type_display', read_only=True)
    time_ago = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'recipient', 'actor', 'actor_id', 'actor_name', 'trip', 'trip_title', 
            'trip_destination', 'notification_type', 'notification_type_display', 'message', 
            'is_read', 'created_at', 'time_ago', 'updated_at', 'invitation'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'recipient', 'invitation']
    
    def get_actor_name(self, obj):
        """Get actor's full name or username"""
        if obj.actor:
            user = obj.actor.user
            return user.get_full_name() or user.username
        return 'System'
    
    def get_time_ago(self, obj):
        """Return human-readable time ago"""
        from django.utils.timezone import now
        from datetime import timedelta
        
        age = now() - obj.created_at
        if age < timedelta(minutes=1):
            return 'just now'
        elif age < timedelta(hours=1):
            minutes = age.seconds // 60
            return f'{minutes}m ago'
        elif age < timedelta(days=1):
            hours = age.seconds // 3600
            return f'{hours}h ago'
        elif age < timedelta(days=7):
            days = age.days
            return f'{days}d ago'
        else:
            return obj.created_at.strftime('%b %d')


class RecommendedTripSerializer(TripSerializer):
    """Extended Trip serializer with recommendation matching scores"""
    match_count = serializers.SerializerMethodField()
    avg_similarity = serializers.SerializerMethodField()
    best_match = serializers.SerializerMethodField()
    recommendation_score = serializers.SerializerMethodField()
    
    class Meta(TripSerializer.Meta):
        fields = TripSerializer.Meta.fields + [
            'match_count', 'avg_similarity', 'best_match', 'recommendation_score'
        ]
    
    def get_match_count(self, obj):
        """Get number of members with good interest match (from context)"""
        return self.context.get('match_data', {}).get(obj.id, {}).get('match_count', 0)
    
    def get_avg_similarity(self, obj):
        """Get average similarity score (from context)"""
        return self.context.get('match_data', {}).get(obj.id, {}).get('avg_similarity', 0.0)
    
    def get_best_match(self, obj):
        """Get best individual match score (from context)"""
        return self.context.get('match_data', {}).get(obj.id, {}).get('best_match', 0.0)
    
    def get_recommendation_score(self, obj):
        """Get weighted recommendation score (from context)"""
        return self.context.get('match_data', {}).get(obj.id, {}).get('score', 0.0)
    
    def get_time_ago(self, obj):
        """Return human-readable time ago"""
        from django.utils.timezone import now
        from datetime import timedelta
        
        age = now() - obj.created_at
        if age < timedelta(minutes=1):
            return 'just now'
        elif age < timedelta(hours=1):
            minutes = age.seconds // 60
            return f'{minutes}m ago'
        elif age < timedelta(days=1):
            hours = age.seconds // 3600
            return f'{hours}h ago'
        elif age < timedelta(days=7):
            days = age.days
            return f'{days}d ago'
        else:
            return obj.created_at.strftime('%b %d')