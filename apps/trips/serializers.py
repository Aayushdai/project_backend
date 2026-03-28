from rest_framework import serializers
from .models import Trip, City, ItineraryItem, Destination
from apps.users.models import UserProfile


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'name', 'country']


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'bio']


class ItineraryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItineraryItem
        fields = ['id', 'day', 'activity', 'notes']


class TripSerializer(serializers.ModelSerializer):
    creator = UserProfileSerializer(read_only=True)
    participants = UserProfileSerializer(many=True, read_only=True)
    itinerary = ItineraryItemSerializer(many=True, read_only=True)
    destination = CitySerializer()

    class Meta:
        model = Trip
        fields = [
            'id', 'title', 'destination', 'start_date', 'end_date',
            'description', 'creator', 'participants', 'is_public',
            'created_at', 'updated_at', 'itinerary'
        ]


class DestinationSerializer(serializers.ModelSerializer):
    city = serializers.StringRelatedField()

    class Meta:
        model = Destination
        fields = '__all__'