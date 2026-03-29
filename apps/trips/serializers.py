from rest_framework import serializers
from .models import Trip, City, ItineraryItem, Destination
from apps.users.models import UserProfile


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

    class Meta:
        model = Trip
        fields = [
            'id', 'title', 'destination', 'destination_id', 'start_date', 'end_date',
            'description', 'creator', 'participants', 'is_public',
            'created_at', 'updated_at', 'itinerary'
        ]

    def create(self, validated_data):
        destination_id = validated_data.pop('destination_id')
        try:
            destination = City.objects.get(id=destination_id)
        except City.DoesNotExist:
            raise serializers.ValidationError({"destination_id": "City not found"})
        
        instance = Trip.objects.create(
            destination=destination,
            **validated_data
        )
        return instance


class DestinationSerializer(serializers.ModelSerializer):
    city = serializers.StringRelatedField()

    class Meta:
        model = Destination
        fields = '__all__'