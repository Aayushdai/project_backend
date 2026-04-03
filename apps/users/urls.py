from django.urls import path
from .views_api import (
    match_users, search_users, get_user_profile, calculate_similarity,
    send_friend_request, get_friend_request_status, respond_friend_request,
    get_pending_friend_requests, cancel_friend_request, get_user_friends,
    unfriend_user, kyc_submission, kyc_pending_list, KYCAdminActionView
)
from . import views_api
from . import views

urlpatterns = [
    path("api/login/", views.frontend_login, name="frontend-login"),
    path("api/register/", views.frontend_register, name="frontend-register"),
    path("api/matches/", match_users),
    path("api/search/", search_users, name="search-users"),
    path("api/user-profile/<int:user_id>/", get_user_profile, name="get-user-profile"),
    path("api/similarity/<int:user_id>/", calculate_similarity, name="calculate-similarity"),
    path("api/friend-request/send/<int:user_id>/", send_friend_request, name="send-friend-request"),
    path("api/friend-request/status/<int:user_id>/", get_friend_request_status, name="friend-request-status"),
    path("api/friend-request/<int:request_id>/respond/", respond_friend_request, name="respond-friend-request"),
    path("api/friend-request/<int:request_id>/cancel/", cancel_friend_request, name="cancel-friend-request"),
    path("api/unfriend/<int:user_id>/", unfriend_user, name="unfriend-user"),
    path("api/friend-requests/pending/", get_pending_friend_requests, name="pending-friend-requests"),
    path("api/friends/", get_user_friends, name="user-friends"),
    path("api/friends/<int:user_id>/", get_user_friends, name="user-friends-by-id"),
    path("api/me/", views.me_view, name="me"),
    path("api/interests/", views.get_interests, name="get-interests"),
    path("api/constraint-tags/", views.get_constraint_tags, name="get-constraint-tags"),
    path("api/profile/update/", views.update_profile_view, name="profile-update"),
    path('api/match/<int:match_id>/action/', views_api.MatchActionView.as_view(), name='match-action'),
    
    # ✅ Password Recovery Endpoints
    path("api/security-questions/", views.get_security_questions, name="get-security-questions"),
    path("api/forgot-password/step1/", views.forgot_password_step1, name="forgot-password-step1"),
    path("api/forgot-password/step2/", views.forgot_password_step2, name="forgot-password-step2"),
    
    # Admin password reset endpoints
    path("api/admin/users/", views.admin_users_list, name="admin-users-list"),
    path("api/admin/reset-password/", views.admin_reset_password, name="admin-reset-password"),
    
    # ✅ KYC Endpoints
    path("api/kyc/", kyc_submission, name="kyc-submission"),
    path("api/kyc/pending/", kyc_pending_list, name="kyc-pending-list"),
    path("api/kyc/<int:profile_id>/action/", KYCAdminActionView.as_view(), name="kyc-admin-action"),
]