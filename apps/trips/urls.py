from django.urls import path
from .views import (
    TripListAPIView, TripDetailAPIView, DestinationListAPIView, DestinationDetailAPIView, 
    CityListAPIView, TripHistoryAPIView, TripExpenseBudgetListAPIView, TripExpenseBudgetDetailAPIView,
    TripReviewListCreateAPIView, JoinTripByInviteCodeAPIView, GenerateInviteLinkAPIView,
    TripInvitationListAPIView, TripInvitationDeleteAPIView, MyInvitationsListAPIView,
    RespondToInvitationAPIView, NotificationListAPIView, UnreadNotificationCountAPIView,
    NotificationMarkAsReadAPIView, NotificationMarkAllAsReadAPIView
)

urlpatterns = [
    path('', TripListAPIView.as_view(), name='trip-list'),
    path('history/', TripHistoryAPIView.as_view(), name='trip-history'),
    path('join/<str:invite_code>/', JoinTripByInviteCodeAPIView.as_view(), name='join-trip-by-code'),
    path('notifications/', NotificationListAPIView.as_view(), name='notifications'),
    path('notifications/unread-count/', UnreadNotificationCountAPIView.as_view(), name='unread-count'),
    path('notifications/read-all/', NotificationMarkAllAsReadAPIView.as_view(), name='read-all-notifications'),
    path('notifications/<int:pk>/read/', NotificationMarkAsReadAPIView.as_view(), name='mark-notification-read'),
    path('invitations/my/', MyInvitationsListAPIView.as_view(), name='my-invitations'),
    path('invitations/<int:pk>/respond/', RespondToInvitationAPIView.as_view(), name='respond-invitation'),
    path('<int:trip_id>/expenses/', TripExpenseBudgetListAPIView.as_view(), name='trip-expenses-list'),
    path('<int:trip_id>/reviews/', TripReviewListCreateAPIView.as_view(), name='trip-reviews'),
    path('<int:trip_id>/generate-invite-link/', GenerateInviteLinkAPIView.as_view(), name='generate-invite-link'),
    path('<int:trip_id>/invitations/', TripInvitationListAPIView.as_view(), name='trip-invitations'),
    path('<int:trip_id>/invitations/<int:pk>/', TripInvitationDeleteAPIView.as_view(), name='trip-invitation-delete'),
    path('<int:pk>/', TripDetailAPIView.as_view(), name='trip-detail'),
    path('expenses/<int:pk>/', TripExpenseBudgetDetailAPIView.as_view(), name='trip-expense-detail'),
    path('destinations/', DestinationListAPIView.as_view(), name='destination-list'),
    path('destinations/<int:id>/', DestinationDetailAPIView.as_view(), name='destination-detail'),
    path('cities/', CityListAPIView.as_view(), name='city-list'),
]