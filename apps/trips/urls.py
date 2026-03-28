from django.urls import path
from .views import TripListAPIView, TripDetailAPIView, DestinationListAPIView, CityListAPIView

urlpatterns = [
    path('trips/', TripListAPIView.as_view(), name='trip-list'),
    path('trips/<int:pk>/', TripDetailAPIView.as_view(), name='trip-detail'),
    path('destinations/', DestinationListAPIView.as_view(), name='destination-list'),
    path('cities/', CityListAPIView.as_view(), name='city-list'),
]