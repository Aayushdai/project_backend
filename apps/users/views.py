from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from apps.users.models import UserProfile
from apps.users.utils import find_similar_users
from django.views.decorators.csrf import csrf_exempt
from .models import UserLoginHistory, User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

import json


@login_required
def profile_view(request, username):
    profile = get_object_or_404(UserProfile, user__username=username)
    return render(request, 'users/profile.html', {'profile': profile})


@login_required
def match_travel_buddies(request):
    profile = request.user.userprofile
    matches = find_similar_users(profile, limit=10, min_similarity=0.6)
    context = {
        'matches': [
            {
                'user': m[0].user,
                'profile': m[0],
                'similarity': m[1] * 100,
            }
            for m in matches
        ],
        'your_profile': profile,
    }
    return render(request, 'users/matches.html', context)


@csrf_exempt
def frontend_login(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Only POST method allowed"})

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "message": "Invalid JSON"}, status=400)

    username = data.get("username")
    password = data.get("password")

    user = authenticate(request, username=username, password=password)
    if user is None:
        return JsonResponse({"success": False, "message": "Invalid credentials"}, status=401)

    # ✅ Check verification status before allowing login
    profile = getattr(user, "userprofile", None)
    if profile:
        if profile.status == "pending":
            return JsonResponse({
                "success": False,
                "status": "pending",
                "message": "Your account is pending admin verification. Please check back later."
            }, status=403)
        if profile.status == "rejected":
            reason = profile.rejection_reason or "Your application did not meet our requirements."
            return JsonResponse({
                "success": False,
                "status": "rejected",
                "message": f"Your account was rejected. Reason: {reason}"
            }, status=403)

    # Approved — issue JWT
    refresh = RefreshToken.for_user(user)
    access  = str(refresh.access_token)

    UserLoginHistory.objects.create(
        user=user,
        ip_address=request.META.get("REMOTE_ADDR"),
        user_agent=request.META.get("HTTP_USER_AGENT")
    )

    return JsonResponse({
        "success": True,
        "message": "Logged in successfully",
        "access": access,
        "user": {
            "id":         user.id,
            "username":   user.username,
            "email":      user.email,
            "first_name": user.first_name,
            "last_name":  user.last_name,
        }
    })


@csrf_exempt
def frontend_register(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Only POST allowed"}, status=405)

    try:
        data  = request.POST
        files = request.FILES

        email      = data.get("email", "").strip().lower()
        password   = data.get("password", "")
        first_name = data.get("first_name", "").strip()
        last_name  = data.get("last_name", "").strip()

        if not email or not password:
            return JsonResponse({"success": False, "message": "Email and password are required"}, status=400)

        if User.objects.filter(email=email).exists():
            return JsonResponse({"success": False, "message": "Email already registered"}, status=400)

        if User.objects.filter(username=email).exists():
            return JsonResponse({"success": False, "message": "User already exists"}, status=400)

        # Create user (inactive until approved — handled via profile.status)
        user = User.objects.create_user(
            username=email,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name,
        )

        try:
            profile = user.userprofile
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=user)

        # Store all registration data for admin review
        profile.status      = 'pending'
        profile.phone       = data.get("phone", "").strip()
        profile.address     = data.get("address", "").strip()
        profile.city        = data.get("city", "").strip()
        profile.country     = data.get("country", "").strip()
        profile.zip_code    = data.get("zip_code", "").strip()
        profile.gender      = data.get("gender", "").strip()
        profile.citizenship = data.get("citizenship", "").strip()
        profile.passport_no = data.get("passport_no", "").strip()
        profile.location    = f"{data.get('city','').strip()}, {data.get('country','').strip()}".strip(", ")

        dob = data.get("dob", "").strip()
        if dob:
            profile.dob = dob

        passport_expiry = data.get("passport_expiry", "").strip()
        if passport_expiry:
            profile.passport_expiry = passport_expiry

        if "profile_photo" in files:
            profile.profile_picture = files["profile_photo"]
        if "passport_photo" in files:
            profile.passport_photo = files["passport_photo"]

        profile.save()

        return JsonResponse({"success": True, "status": "pending", "message": "Registration submitted. Awaiting admin verification."})

    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me_view(request):
    user    = request.user
    profile = getattr(user, "userprofile", None)
    pic = None
    if profile and profile.profile_picture:
        pic = request.build_absolute_uri(profile.profile_picture.url)
    return Response({
        "id":          user.id,
        "username":    user.username,
        "first_name":  user.first_name,
        "last_name":   user.last_name,
        "email":       user.email,
        "date_joined": user.date_joined,
        "profile_picture":          pic,
        "bio":                      profile.bio                     if profile else "",
        "location":                 profile.location                if profile else "",
        "travel_style":             profile.travel_style            if profile else "",
        "pace":                     profile.pace                    if profile else "",
        "accommodation_preference": profile.accomodation_preference if profile else "",
        "budget_level":             profile.budget_level            if profile else 5,
        "adventure_level":          profile.adventure_level         if profile else 5,
        "social_level":             profile.social_level            if profile else 5,
        "trips_count":     0,
        "buddies_count":   0,
        "countries_count": 0,
        "rating":          None,
    })


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_profile_view(request):
    user    = request.user
    profile = getattr(user, "userprofile", None)
    if not profile:
        return Response({"message": "Profile not found."}, status=404)

    if "first_name" in request.data:
        user.first_name = request.data["first_name"]
    if "last_name" in request.data:
        user.last_name = request.data["last_name"]
    user.save()

    for field in ["bio", "location", "travel_style", "pace", "budget_level", "adventure_level", "social_level"]:
        if field in request.data:
            setattr(profile, field, request.data[field])

    if "accommodation_preference" in request.data:
        profile.accomodation_preference = request.data["accommodation_preference"]

    if "profile_photo" in request.FILES:
        profile.profile_picture = request.FILES["profile_photo"]

    profile.save()

    pic = request.build_absolute_uri(profile.profile_picture.url) if profile.profile_picture else None
    return Response({
        "message":      "Updated.",
        "first_name":   user.first_name,
        "last_name":    user.last_name,
        "profile_picture": pic,
        "bio":          profile.bio,
        "location":     profile.location,
        "travel_style": profile.travel_style,
        "pace":         profile.pace,
        "accommodation_preference": profile.accomodation_preference,
        "budget_level":    profile.budget_level,
        "adventure_level": profile.adventure_level,
        "social_level":    profile.social_level,
    })