from rest_framework.decorators import api_view,permission_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from .utils import find_similar_users, calculate_user_similarity
from .models import Match, UserProfile, FriendRequest
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.db.models import Q


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def match_users(request):
    try:
        profile = request.user.userprofile
    except  UserProfile.DoesNotExist:
        return Response({"detail": "User profile not found"}, status=404)
    matches = find_similar_users(profile)

    result = []

    for user, similarity in matches:

        result.append({
            "username": user.user.username,
            "similarity": similarity
        })

    return Response(result)
class MatchActionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, match_id):
        match = get_object_or_404(Match, id=match_id)

        # Security: only the receiver can accept/reject
        if match.user2 != request.user:
            return Response({"detail": "Not authorized"}, status=403)

        action = request.data.get("action").lower() # "accept" or "reject"

        if action == "accept":
            match.status = "accepted"
            match.save()
            # Optional: create reverse match or chat room here
            return Response({"status": "accepted"})

        elif action == "reject":
            match.status = "rejected"
            match.save()
            return Response({"status": "rejected"})

        return Response({"detail": "Invalid action"}, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_users(request):
    """Search users by username, first name, or last name"""
    query = request.query_params.get('q', '').strip()
    
    if not query or len(query) < 2:
        return Response({"results": []})
    
    # Search by username, first_name, or last_name
    users = User.objects.filter(
        Q(username__icontains=query) |
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query)
    ).exclude(id=request.user.id)[:20]  # Limit to 20 results
    
    results = []
    for user in users:
        profile_pic = None
        try:
            profile = user.userprofile
            if profile.profile_picture:
                profile_pic = profile.profile_picture.url
        except UserProfile.DoesNotExist:
            pass
        
        results.append({
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "profile_picture": profile_pic,
            "location": profile.location if 'profile' in locals() else ""
        })
    
    return Response({"results": results})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request, user_id):
    """Get public profile details of a user by ID"""
    try:
        user = User.objects.get(id=user_id)
        profile = user.userprofile
    except (User.DoesNotExist, UserProfile.DoesNotExist):
        return Response({"detail": "User profile not found"}, status=404)
    
    profile_pic = profile.profile_picture.url if profile.profile_picture else None
    
    return Response({
        "id": user.id,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "profile_picture": profile_pic,
        "bio": profile.bio,
        "location": profile.location,
        "preferred_destinations": profile.preferred_destinations,
        "travel_style": profile.travel_style,
        "pace": profile.pace,
        "accomodation_preference": profile.accomodation_preference,
        "budget_level": profile.budget_level,
        "adventure_level": profile.adventure_level,
        "social_level": profile.social_level,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def calculate_similarity(request, user_id):
    """Calculate similarity score between current user and target user (0-100%)"""
    try:
        current_profile = request.user.userprofile
        target_user = User.objects.get(id=user_id)
        target_profile = target_user.userprofile
    except (UserProfile.DoesNotExist, User.DoesNotExist):
        return Response({"detail": "User profile not found"}, status=404)
    
    similarity_score = calculate_user_similarity(current_profile, target_profile)
    
    return Response({
        "similarity": similarity_score,
        "username": target_user.username,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_friend_request(request, user_id):
    """Send a friend request to another user"""
    try:
        to_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"detail": "User not found"}, status=404)
    
    if to_user == request.user:
        return Response({"detail": "Cannot send friend request to yourself"}, status=400)
    
    # Check if request already exists
    existing_request = FriendRequest.objects.filter(
        from_user=request.user,
        to_user=to_user
    ).first()
    
    if existing_request:
        return Response({
            "detail": f"Friend request already {existing_request.status}",
            "status": existing_request.status
        }, status=400)
    
    # Check for reverse request (to_user sent to request.user)
    reverse_request = FriendRequest.objects.filter(
        from_user=to_user,
        to_user=request.user,
        status='pending'
    ).first()
    
    if reverse_request:
        # Auto-accept if there's a pending request from them
        reverse_request.status = 'accepted'
        reverse_request.save()
        
        # Create a request from current user too
        friend_request = FriendRequest.objects.create(
            from_user=request.user,
            to_user=to_user,
            status='accepted'
        )
        return Response({
            "detail": "Friend request accepted and mutual friendship created",
            "status": "accepted",
            "type": "outgoing",
            "request_id": friend_request.id
        }, status=201)
    
    # Create new friend request
    friend_request = FriendRequest.objects.create(
        from_user=request.user,
        to_user=to_user,
        status='pending'
    )
    
    return Response({
        "detail": "Friend request sent",
        "status": "pending",
        "type": "outgoing",
        "request_id": friend_request.id
    }, status=201)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_friend_request_status(request, user_id):
    """Get friend request status between current user and another user"""
    try:
        target_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"detail": "User not found"}, status=404)
    
    # Check for request from current user to target
    outgoing = FriendRequest.objects.filter(
        from_user=request.user,
        to_user=target_user
    ).first()
    
    # Check for request from target to current user
    incoming = FriendRequest.objects.filter(
        from_user=target_user,
        to_user=request.user
    ).first()
    
    # Determine overall status
    if outgoing and outgoing.status == 'accepted':
        return Response({"status": "friends", "type": "outgoing", "request_id": outgoing.id})
    elif incoming and incoming.status == 'accepted':
        return Response({"status": "friends", "type": "incoming", "request_id": incoming.id})
    elif outgoing and outgoing.status == 'pending':
        return Response({"status": "pending", "type": "outgoing", "request_id": outgoing.id})
    elif incoming and incoming.status == 'pending':
        return Response({"status": "pending", "type": "incoming", "request_id": incoming.id})
    else:
        return Response({"status": "none"})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def respond_friend_request(request, request_id):
    """Accept or reject a friend request"""
    try:
        friend_request = FriendRequest.objects.get(id=request_id)
    except FriendRequest.DoesNotExist:
        return Response({"detail": "Friend request not found"}, status=404)
    
    if friend_request.to_user != request.user:
        return Response({"detail": "Not authorized to respond to this request"}, status=403)
    
    action = request.data.get('action', '').lower()
    
    if action == 'accept':
        friend_request.status = 'accepted'
        friend_request.save()
        
        # Create reverse request if it doesn't exist
        reverse = FriendRequest.objects.filter(
            from_user=friend_request.to_user,
            to_user=friend_request.from_user
        ).first()
        
        if not reverse:
            FriendRequest.objects.create(
                from_user=friend_request.to_user,
                to_user=friend_request.from_user,
                status='accepted'
            )
        
        return Response({"detail": "Friend request accepted", "status": "accepted"})
    
    elif action == 'reject':
        friend_request.status = 'rejected'
        friend_request.save()
        return Response({"detail": "Friend request rejected", "status": "rejected"})
    
    else:
        return Response({"detail": "Invalid action"}, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_pending_friend_requests(request):
    """Get all pending friend requests for current user"""
    pending_requests = FriendRequest.objects.filter(
        to_user=request.user,
        status='pending'
    ).select_related('from_user')
    
    print(f"DEBUG: User {request.user.username} - Found {pending_requests.count()} pending requests")
    
    requests_data = []
    for freq in pending_requests:
        try:
            profile = freq.from_user.userprofile
            profile_pic = profile.profile_picture.url if profile.profile_picture else None
        except UserProfile.DoesNotExist:
            profile_pic = None
        
        requests_data.append({
            "id": freq.id,
            "from_user_id": freq.from_user.id,
            "username": freq.from_user.username,
            "first_name": freq.from_user.first_name,
            "last_name": freq.from_user.last_name,
            "profile_picture": profile_pic,
            "created_at": freq.created_at,
            "request_id": freq.id
        })
    
    return Response({"pending_requests": requests_data})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_friend_request(request, request_id):
    """Cancel an outgoing friend request"""
    try:
        friend_request = FriendRequest.objects.get(id=request_id)
    except FriendRequest.DoesNotExist:
        return Response({"detail": "Friend request not found"}, status=404)
    
    # Only the sender can cancel their own request
    if friend_request.from_user != request.user:
        return Response({"detail": "Not authorized to cancel this request"}, status=403)
    
    # Only cancel pending requests
    if friend_request.status != 'pending':
        return Response({"detail": "Can only cancel pending requests"}, status=400)
    
    friend_request.delete()
    return Response({"detail": "Friend request cancelled", "status": "none"})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_friends(request, user_id=None):
    """Get all friends of a user (both incoming and outgoing accepted requests)"""
    if user_id is None:
        target_user = request.user
    else:
        try:
            target_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found"}, status=404)
    
    # Get all accepted friend requests involving this user
    outgoing_friends = FriendRequest.objects.filter(
        from_user=target_user,
        status='accepted'
    ).select_related('to_user')
    
    incoming_friends = FriendRequest.objects.filter(
        to_user=target_user,
        status='accepted'
    ).select_related('from_user')
    
    friends_data = []
    friends_ids = set()
    
    # Add friends from outgoing requests
    for freq in outgoing_friends:
        friend_user = freq.to_user
        if friend_user.id not in friends_ids:
            try:
                profile = friend_user.userprofile
                profile_pic = profile.profile_picture.url if profile.profile_picture else None
            except UserProfile.DoesNotExist:
                profile_pic = None
            
            friends_data.append({
                "id": friend_user.id,
                "username": friend_user.username,
                "first_name": friend_user.first_name,
                "last_name": friend_user.last_name,
                "profile_picture": profile_pic,
            })
            friends_ids.add(friend_user.id)
    
    # Add friends from incoming requests
    for freq in incoming_friends:
        friend_user = freq.from_user
        if friend_user.id not in friends_ids:
            try:
                profile = friend_user.userprofile
                profile_pic = profile.profile_picture.url if profile.profile_picture else None
            except UserProfile.DoesNotExist:
                profile_pic = None
            
            friends_data.append({
                "id": friend_user.id,
                "username": friend_user.username,
                "first_name": friend_user.first_name,
                "last_name": friend_user.last_name,
                "profile_picture": profile_pic,
            })
            friends_ids.add(friend_user.id)
    
    return Response({"friends": friends_data, "friends_count": len(friends_data)})