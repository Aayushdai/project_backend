from rest_framework import serializers
from .models import UserProfile, Interest, ConstraintTag


class InterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interest
        fields = ['id', 'name', 'description', 'category']


class ConstraintTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConstraintTag
        fields = ['id', 'name', 'category', 'description']


class UserProfileSerializer(serializers.ModelSerializer):
    interests = InterestSerializer(many=True, read_only=True)
    interest_ids = serializers.PrimaryKeyRelatedField(
        queryset=Interest.objects.all(),
        write_only=True,
        many=True,
        source='interests'
    )
    constraint_tags = ConstraintTagSerializer(many=True, read_only=True)
    constraint_tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=ConstraintTag.objects.all(),
        write_only=True,
        many=True,
        source='constraint_tags'
    )

    class Meta:
        model = UserProfile

        fields = [
            'id',
            'user',
            'bio',
            'location',
            'travel_style',
            'pace',
            'accommodation_preference',
            'budget_level',
            'adventure_level',
            'social_level',
            'interests',
            'interest_ids',
            'constraint_tags',
            'constraint_tag_ids',
            'min_match_age',
            'max_match_age',
        ]