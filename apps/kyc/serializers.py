from rest_framework import serializers
from .models import KYCProfile


class KYCSimpleSerializer(serializers.ModelSerializer):
    """Used for listing / basic info"""
    class Meta:
        model = KYCProfile
        fields = ['id', 'status', 'submitted_at', 'full_name']


class KYCProfileSerializer(serializers.ModelSerializer):
    """Full serializer for submission and detail"""
    class Meta:
        model = KYCProfile
        fields = [
            'id', 'user', 'status', 'submitted_at', 'reviewed_at',
            'full_name', 'date_of_birth', 'nationality', 'id_number',
            'address', 'city', 'country',
            'id_document', 'selfie', 'proof_of_address',
            'proof_of_address_type',
            'proof_of_address_date',
            'notes'
        ]
        read_only_fields = ['user', 'status', 'submitted_at', 'reviewed_at', 'reviewed_by']


class KYCReviewSerializer(serializers.ModelSerializer):
    """Admin/Staff serializer to review and update status"""
    class Meta:
        model = KYCProfile
        fields = ['status', 'notes']
        extra_kwargs = {
            'status': {'required': True}
        }