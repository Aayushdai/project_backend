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

# ✅ Allowed email domains
ALLOWED_EMAIL_DOMAINS = {
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "protonmail.com",
    "icloud.com", "mail.com", "yandex.com", "zoho.com", "gmx.com", "aol.com",
    "tutanota.com", "mailbox.org", "fastmail.com", "posteo.de", "hey.com",
}

def validate_email_domain(email):
    """Validate that email is from an allowed domain."""
    try:
        domain = email.split("@")[1].lower()
        if domain not in ALLOWED_EMAIL_DOMAINS:
            return False, f"Email domain must be one of the allowed providers (Gmail, Yahoo, Hotmail, etc.)"
        return True, ""
    except:
        return False, "Invalid email format"


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
            "is_staff":   user.is_staff,
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

        # ✅ Validate email domain
        is_valid, domain_error = validate_email_domain(email)
        if not is_valid:
            return JsonResponse({"success": False, "message": domain_error}, status=400)

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

        # ✅ Auto-approve user for development (can be changed to manual approval in production)
        profile.status = 'approved'
        profile.save()

        # ✅ Store security questions and answers
        from django.contrib.auth.hashers import make_password
        from .models import UserSecurityAnswer
        
        security_answers_str = data.get("security_questions", "{}")
        try:
            import json
            security_answers_data = json.loads(security_answers_str) if isinstance(security_answers_str, str) else security_answers_str
            
            if security_answers_data:
                # Hash the answers before storing
                hashed_answers = {}
                for question_id_str, answer in security_answers_data.items():
                    # Normalize answer: strip, lowercase
                    normalized_answer = answer.strip().lower()
                    # Hash it
                    hashed_answers[question_id_str] = make_password(normalized_answer)
                
                # Create or update UserSecurityAnswer
                security_obj, created = UserSecurityAnswer.objects.update_or_create(
                    user=user,
                    defaults={"questions_answers": hashed_answers}
                )
        except Exception as e:
            print(f"Error storing security questions: {e}")

        # ✅ Log the user in immediately
        login(request, user)
        
        # Issue JWT token
        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)

        # Send registration confirmation email
        try:
            from core.email_service import EmailService
            EmailService.send_registration_confirmation(user.email, user.first_name)
        except Exception as e:
            print(f"Error sending email: {e}")

        return JsonResponse({
            "success": True,
            "status": "approved",
            "message": "Registration successful!",
            "access": access,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_staff": user.is_staff,
            }
        })

    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)


@api_view(["GET"])
def get_interests(request):
    """Get all available interests for matching"""
    from .models import Interest
    from .serializers import InterestSerializer
    interests = Interest.objects.all()
    serializer = InterestSerializer(interests, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def get_constraint_tags(request):
    """Get all available constraint tags (diet, lifestyle, values, age ranges)"""
    from .models import ConstraintTag
    from .serializers import ConstraintTagSerializer
    tags = ConstraintTag.objects.all()
    serializer = ConstraintTagSerializer(tags, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me_view(request):
    user    = request.user
    profile = getattr(user, "userprofile", None)
    pic = None
    if profile and profile.profile_picture:
        pic = request.build_absolute_uri(profile.profile_picture.url)
    return Response({
        "id":          profile.id if profile else user.id,  # ✅ Return UserProfile ID, not User ID
        "user_id":     user.id,  # Also provide User ID if needed
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

    # ✅ Handle interests
    if "interest_ids" in request.data:
        interest_ids = request.data.get("interest_ids", [])
        if isinstance(interest_ids, list):
            profile.interests.set(interest_ids)

    # ✅ Handle constraint tags
    if "constraint_tag_ids" in request.data:
        constraint_tag_ids = request.data.get("constraint_tag_ids", [])
        if isinstance(constraint_tag_ids, list):
            profile.constraint_tags.set(constraint_tag_ids)

    # ✅ Handle age preferences
    if "min_match_age" in request.data:
        profile.min_match_age = request.data["min_match_age"]
    if "max_match_age" in request.data:
        profile.max_match_age = request.data["max_match_age"]

    if "profile_photo" in request.FILES:
        profile.profile_picture = request.FILES["profile_photo"]

    profile.save()

    pic = request.build_absolute_uri(profile.profile_picture.url) if profile.profile_picture else None
    interests = [{"id": i.id, "name": i.name} for i in profile.interests.all()]
    constraint_tags = [{"id": t.id, "name": t.name, "category": t.category} for t in profile.constraint_tags.all()]
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
        "interests":       interests,
        "constraint_tags": constraint_tags,
        "min_match_age":   profile.min_match_age,
        "max_match_age":   profile.max_match_age,
    })


# ============================================
# ADMIN PASSWORD RESET ENDPOINTS
# ============================================

import string
import secrets

def generate_temporary_password(length=12):
    """Generate a secure temporary password"""
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_users_list(request):
    """Get list of users for admin dashboard - only admins can access"""
    if not request.user.is_staff:
        return Response({"error": "Only admins can access this"}, status=403)
    
    # Get search query from params
    search_query = request.query_params.get('search', '').strip()
    page = int(request.query_params.get('page', 1))
    page_size = int(request.query_params.get('page_size', 20))
    
    # Filter users
    users_qs = User.objects.all().select_related('userprofile')
    
    if search_query:
        from django.db.models import Q
        users_qs = users_qs.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    total_count = users_qs.count()
    
    # Pagination
    start = (page - 1) * page_size
    end = start + page_size
    users = users_qs[start:end]
    
    users_data = []
    for user in users:
        profile = getattr(user, 'userprofile', None)
        users_data.append({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "date_joined": user.date_joined,
            "is_staff": user.is_staff,
            "is_active": user.is_active,
            "profile_status": profile.status if profile else "no_profile",
        })
    
    return Response({
        "total": total_count,
        "page": page,
        "page_size": page_size,
        "users": users_data
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def admin_reset_password(request):
    """Reset a user's password and return temporary password - only admins can use"""
    if not request.user.is_staff:
        return Response({"error": "Only admins can reset passwords"}, status=403)
    
    user_id = request.data.get('user_id')
    
    if not user_id:
        return Response({"error": "user_id is required"}, status=400)
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)
    
    # Generate temporary password
    temp_password = generate_temporary_password()
    
    # Set the new password
    user.set_password(temp_password)
    user.save()
    
    return Response({
        "success": True,
        "message": f"Password reset for {user.username}",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
        },
        "temporary_password": temp_password,
        "instructions": "Share this temporary password with the user. They should change it after their first login."
    })


# ✅ ========== PASSWORD RECOVERY ENDPOINTS ==========

@api_view(["GET"])
def get_security_questions(request):
    """Get all available security questions for password recovery"""
    from .models import SecurityQuestion
    questions = SecurityQuestion.objects.all().values('id', 'question', 'category')
    return Response(list(questions))


@csrf_exempt
def forgot_password_step1(request):
    """Step 1: User enters email and gets their security questions"""
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body)
        email = data.get("email", "").strip().lower()

        if not email:
            return JsonResponse({"success": False, "message": "Email is required"}, status=400)

        # ✅ Validate email domain
        is_valid, domain_error = validate_email_domain(email)
        if not is_valid:
            return JsonResponse({"success": False, "message": domain_error}, status=400)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return JsonResponse({"success": False, "message": "Email not found"}, status=404)

        # Get user's security answers
        try:
            security_answers = user.security_answers
            question_ids = list(security_answers.questions_answers.keys())
        except:
            return JsonResponse({
                "success": False,
                "message": "No security questions set. Please contact support."
            }, status=400)

        # Get the questions
        from .models import SecurityQuestion
        questions = SecurityQuestion.objects.filter(id__in=question_ids).values('id', 'question')

        return JsonResponse({
            "success": True,
            "email": email,
            "questions": list(questions),
            "message": "Answer your security questions to reset your password"
        })

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "message": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)


@csrf_exempt
def forgot_password_step2(request):
    """Step 2: Verify security answers and reset password"""
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body)
        email = data.get("email", "").strip().lower()
        answers_provided = data.get("answers", {})  # {question_id: answer_text}
        new_password = data.get("new_password", "")

        if not email or not answers_provided or not new_password:
            return JsonResponse({
                "success": False,
                "message": "Email, answers, and new password are required"
            }, status=400)

        # ✅ Validate email domain
        is_valid, domain_error = validate_email_domain(email)
        if not is_valid:
            return JsonResponse({"success": False, "message": domain_error}, status=400)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return JsonResponse({"success": False, "message": "User not found"}, status=404)

        # Get user's security answers
        try:
            security_answers = user.security_answers
        except:
            return JsonResponse({
                "success": False,
                "message": "Security answers not found"
            }, status=400)

        # Hash the provided answers and verify
        from django.contrib.auth.hashers import check_password
        correct_count = 0
        total_count = len(security_answers.questions_answers)

        for question_id_str, stored_hash in security_answers.questions_answers.items():
            provided_answer = answers_provided.get(question_id_str, "").strip().lower()
            if check_password(provided_answer, stored_hash):
                correct_count += 1

        # Require ALL answers to be correct
        if correct_count != total_count:
            return JsonResponse({
                "success": False,
                "message": f"Incorrect answers. {correct_count}/{total_count} answers were correct."
            }, status=400)

        # ✅ All answers correct - reset password
        user.set_password(new_password)
        user.save()

        return JsonResponse({
            "success": True,
            "message": "Password reset successfully! Please login with your new password."
        })

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "message": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)