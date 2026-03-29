from django.urls import path
from .views_api import match_users
from . import views_api
from . import views

urlpatterns = [
    path("api/login/", views.frontend_login, name="frontend-login"),
    path("api/register/", views.frontend_register, name="frontend-register"),
    path("api/matches/", match_users),
    path("api/me/", views.me_view, name="me"),
    path("api/interests/", views.get_interests, name="get-interests"),
    path("api/constraint-tags/", views.get_constraint_tags, name="get-constraint-tags"),
    path("api/profile/update/", views.update_profile_view, name="profile-update"),
    path('api/match/<int:match_id>/action/', views_api.MatchActionView.as_view(), name='match-action'),
    
    # Admin password reset endpoints
    path("api/admin/users/", views.admin_users_list, name="admin-users-list"),
    path("api/admin/reset-password/", views.admin_reset_password, name="admin-reset-password"),
]