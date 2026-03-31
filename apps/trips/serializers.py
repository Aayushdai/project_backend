from rest_framework import serializers
from .models import Trip, City, ItineraryItem, Destination
from apps.users.models import UserProfile, ConstraintTag


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


class TripSerializer(serializers.ModelSerializer):
    creator = UserProfileSerializer(read_only=True)
    participants = UserProfileSerializer(many=True, read_only=True)
    itinerary = ItineraryItemSerializer(many=True, read_only=True)
    destination = CitySerializer(read_only=True)  # Read: nested object
    destination_id = serializers.IntegerField(write_only=True)  # Write: just ID
    constraint_tags = ConstraintTagSerializer(many=True, read_only=True)
    constraint_tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=ConstraintTag.objects.all(),
        write_only=True,
        many=True,
        required=False
    )

    class Meta:
        model = Trip
        fields = [
            'id', 'title', 'destination', 'destination_id', 'start_date', 'end_date',
            'description', 'creator', 'participants', 'constraint_tags', 'constraint_tag_ids',
            'is_public', 'created_at', 'updated_at', 'itinerary'
        ]

    def create(self, validated_data):
        destination_id = validated_data.pop('destination_id')
        constraint_tag_ids = validated_data.pop('constraint_tag_ids', [])
        
        try:
            destination = City.objects.get(id=destination_id)
        except City.DoesNotExist:
            raise serializers.ValidationError({"destination_id": "City not found"})
        
        instance = Trip.objects.create(
            destination=destination,
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