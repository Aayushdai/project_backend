from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('api/stats/', views.api_stats, name='api_stats'),
    path('stats/', views.stats_dashboard, name='stats_dashboard'),  # Full page if needed
]

