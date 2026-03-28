from django.urls import path
from .views_api import match_users
from . import views_api
from . import views

urlpatterns = [
    path("api/login/", views.frontend_login, name="frontend-login"),
    path("api/register/", views.frontend_register, name="frontend-register"),
    path("api/matches/", match_users),
    path("api/me/", views.me_view, name="me"),
    path("api/profile/update/", views.update_profile_view, name="profile-update"),
    path('api/match/<int:match_id>/action/', views_api.MatchActionView.as_view(), name='match-action'),
]