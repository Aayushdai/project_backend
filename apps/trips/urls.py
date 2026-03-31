from django.urls import path
from .views import TripListAPIView, TripDetailAPIView, DestinationListAPIView, DestinationDetailAPIView, CityListAPIView, TripHistoryAPIView

urlpatterns = [
    path('trips/', TripListAPIView.as_view(), name='trip-list'),
    path('trips/<int:pk>/', TripDetailAPIView.as_view(), name='trip-detail'),
    path('trip-history/', TripHistoryAPIView.as_view(), name='trip-history'),
    path('destinations/', DestinationListAPIView.as_view(), name='destination-list'),
    path('destinations/<int:id>/', DestinationDetailAPIView.as_view(), name='destination-detail'),
    path('cities/', CityListAPIView.as_view(), name='city-list'),
]