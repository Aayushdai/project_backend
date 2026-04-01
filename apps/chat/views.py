from rest_framework import serializers, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import ChatMessage
from apps.users.models import UserProfile
from apps.trips.models import City, Destination
from apps.kyc.permissions import IsKYCApproved


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
    permission_classes = [IsAuthenticated, IsKYCApproved]
    
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
        
        # Generate response (now returns structured data)
        response_data = self.generate_response(message)
        response_text = response_data.get('response', '')
        
        # Save chat message
        chat_msg = ChatMessage.objects.create(
            user=user_profile,
            message=message,
            response=response_text
        )
        
        serializer = self.get_serializer(chat_msg)
        
        # Return response with additional metadata for frontend
        return Response({
            **serializer.data,
            'response_metadata': {
                'type': response_data.get('type', 'default'),
                'links': response_data.get('links', [])
            }
        }, status=status.HTTP_201_CREATED)
    
    def generate_response(self, message):
        """Generate a response based on the message with optional clickable keywords"""
        message_lower = message.lower()
        
        # Check if user specifically asking for map
        map_specific_keywords = ['map', 'explore', 'show map', 'where is the map', 'where\'s the map']
        is_asking_for_map = any(keyword in message_lower for keyword in map_specific_keywords)
        
        # Keywords that indicate destination queries (not just map)
        destination_keywords = ['destination', 'location', 'visit', 'go to', 'where is']
        is_destination_query = any(keyword in message_lower for keyword in destination_keywords)
        
        # Check if user is asking about specific destinations or cities
        destinations = Destination.objects.all()
        cities = City.objects.all()
        
        mentioned_destinations = []
        mentioned_cities = []
        
        # Check for mentioned destinations
        for dest in destinations:
            if dest.name.lower() in message_lower:
                mentioned_destinations.append(dest)
        
        # Check for mentioned cities
        for city in cities:
            if city.name.lower() in message_lower:
                mentioned_cities.append(city)
        
        # If user specifically asks for map, redirect to Explore page
        if is_asking_for_map and not mentioned_destinations and not mentioned_cities:
            return {
                'response': "Let me take you to the map where you can explore all destinations! Click below to see the interactive map.",
                'type': 'map',
                'links': [
                    {'keyword': 'map', 'route': '/explore', 'type': 'action'}
                ]
            }
        
        # If user asks about specific destinations/locations, provide those
        if mentioned_destinations or mentioned_cities:
            response_data = {
                'response': '',
                'type': 'destination',
                'links': []
            }
            
            if mentioned_destinations:
                dest_names = ', '.join([f"**{d.name}**" for d in mentioned_destinations])
                response_data['response'] = (
                    f"Great choice! You're interested in {dest_names}. "
                    f"Click on any location to view more details and explore trips!"
                )
                for dest in mentioned_destinations:
                    response_data['links'].append({
                        'keyword': dest.name,
                        'route': f'/destination/{dest.id}',
                        'type': 'destination'
                    })
            
            if mentioned_cities:
                city_names = ', '.join([f"**{c.name}**" for c in mentioned_cities])
                response_data['response'] += (
                    f"\n\nYou can also explore all trips in {city_names}. "
                    f"Click on any city to see available trips!"
                )
                for city in mentioned_cities:
                    response_data['links'].append({
                        'keyword': city.name,
                        'route': f'/city/{city.id}',
                        'type': 'city'
                    })
            
            # Add link to explore all destinations
            response_data['response'] += "\n\nOr visit the **map** to see all destinations!"
            response_data['links'].append({
                'keyword': 'map',
                'route': '/explore',
                'type': 'action'
            })
            
            return response_data
        
        # Greetings
        if any(word in message_lower for word in ['hello', 'hi', 'hey']):
            return {
                'response': "Hello! How can I assist you with your travel plans today? You can ask me about destinations, create a trip, or explore the **map**.",
                'type': 'greeting',
                'links': [
                    {'keyword': 'map', 'route': '/explore', 'type': 'action'}
                ]
            }
        
        # Trip planning
        if any(word in message_lower for word in ['trip', 'plan', 'travel', 'create']):
            return {
                'response': "I can help you plan your trip! You can **create a new trip**, **browse destinations**, or get suggestions. What would you like to do?",
                'type': 'trip',
                'links': [
                    {'keyword': 'create a new trip', 'route': '/create-trip', 'type': 'action'},
                    {'keyword': 'browse destinations', 'route': '/explore', 'type': 'action'}
                ]
            }
        
        # Expense tracking
        if any(word in message_lower for word in ['expense', 'cost', 'budget', 'price']):
            return {
                'response': "You can track expenses for your trips on the **Dashboard**. Would you like help managing your trip budget?",
                'type': 'expense',
                'links': [
                    {'keyword': 'Dashboard', 'route': '/dashboard', 'type': 'action'}
                ]
            }
        
        # Thanks
        if any(word in message_lower for word in ['thank', 'thanks']):
            return {
                'response': "You're welcome! Feel free to ask me anything about your travels.",
                'type': 'thanks',
                'links': []
            }
        
        # Default response
        return {
            'response': (
                "I'm here to help with travel planning! You can ask me about **trips**, **destinations**, "
                "**expenses**, or view the **map**. What can I help you with?"
            ),
            'type': 'default',
            'links': [
                {'keyword': 'map', 'route': '/explore', 'type': 'action'},
                {'keyword': 'trips', 'route': '/dashboard', 'type': 'action'},
                {'keyword': 'destinations', 'route': '/explore', 'type': 'action'}
            ]
        }

