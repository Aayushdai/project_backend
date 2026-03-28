from rest_framework import serializers, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import ChatMessage
from apps.users.models import UserProfile


class ChatMessageSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatMessage
        fields = ['id', 'user', 'username', 'message', 'response', 'created_at']
        read_only_fields = ['user', 'response', 'created_at']
    
    def get_username(self, obj):
        return obj.user.user.username if obj.user else None


class ChatViewSet(viewsets.ModelViewSet):
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user_profile = UserProfile.objects.get(user=self.request.user)
        return ChatMessage.objects.filter(user=user_profile).order_by('-created_at')
    
    @action(detail=False, methods=['post'])
    def chat(self, request):
        """Handle chat messages"""
        message = request.data.get('message', '').strip()
        
        if not message:
            return Response(
                {'error': 'Message cannot be empty'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get user profile
        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            return Response(
                {'error': 'User profile not found'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Simple response logic - you can improve this
        response_text = self.generate_response(message)
        
        # Save chat message
        chat_msg = ChatMessage.objects.create(
            user=user_profile,
            message=message,
            response=response_text
        )
        
        serializer = self.get_serializer(chat_msg)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def generate_response(self, message):
        """Generate a response based on the message"""
        message_lower = message.lower()
        
        # Simple keyword matching for now
        if any(word in message_lower for word in ['hello', 'hi', 'hey']):
            return "Hello! How can I assist you with your travel plans today?"
        
        if any(word in message_lower for word in ['trip', 'plan', 'travel']):
            return "I can help you plan your trip! Would you like to create a new trip, browse destinations, or get suggestions?"
        
        if any(word in message_lower for word in ['destination', 'where', 'explore']):
            return "You can explore destinations on our map or check the Explore page. Would you like recommendations?"
        
        if any(word in message_lower for word in ['expense', 'cost', 'budget', 'price']):
            return "You can track expenses for your trips on the Dashboard. Would you like help managing your trip budget?"
        
        if any(word in message_lower for word in ['thank', 'thanks']):
            return "You're welcome! Feel free to ask me anything about your travels."
        
        # Default response
        return "I'm here to help with travel planning! You can ask me about trips, destinations, expenses, or anything related to Travel Companion."

