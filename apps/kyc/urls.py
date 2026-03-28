from django.urls import path
from .views import KYCListCreateView, KYCDetailView, KYCReviewView

urlpatterns = [
    path('', KYCListCreateView.as_view(), name='kyc-list-create'),
    path('<int:id>/', KYCDetailView.as_view(), name='kyc-detail'),
    path('<int:id>/review/', KYCReviewView.as_view(), name='kyc-review'),
]