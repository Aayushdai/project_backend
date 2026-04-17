from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
from apps.trips.models import Trip
from apps.kyc.models import KYCProfile
from django.db.models import Count, Q
from datetime import date, timedelta
import json

def home(request):
    return HttpResponse("Welcome to Travel Companion!")

@require_http_methods(["GET"])
def stats_dashboard(request):
    """Render the full statistics dashboard page"""
    return render(request, 'stats_dashboard.html')

@require_http_methods(["GET"])
def api_stats(request):
    """API endpoint to fetch real statistics data"""
    try:
        # Total users
        total_users = User.objects.count()
        
        # Active users (users with logged in within last 30 days or have active trips)
        thirty_days_ago = date.today() - timedelta(days=30)
        active_users = User.objects.filter(
            Q(userloginhistory__login_time__gte=thirty_days_ago) |
            Q(userprofile__joined_trips__end_date__gte=date.today())
        ).distinct().count()
        
        # Deleted accounts (soft delete - users with is_active=False)
        deleted_accounts = User.objects.filter(is_active=False).count()
        
        # Trip statistics
        total_trips = Trip.objects.count()
        completed_trips = Trip.objects.filter(is_completed=True).count()
        
        # KYC verification statistics
        verified_users = KYCProfile.objects.filter(status='approved').count()
        non_verified_users = User.objects.exclude(
            kyc_profile__status='approved'
        ).count()
        
        # Monthly growth data (last 6 months)
        months = []
        total_users_data = []
        active_users_data = []
        deleted_accounts_data = []
        total_trips_data = []
        completed_trips_data = []
        verified_data = []
        unverified_data = []
        
        for i in range(5, -1, -1):
            # Calculate date range for this month
            end_date = date.today() - timedelta(days=i*30)
            start_date = end_date - timedelta(days=30)
            
            # Month label
            month_label = end_date.strftime('%b')
            months.append(month_label)
            
            # Users created up to this month
            users_count = User.objects.filter(date_joined__lte=end_date).count()
            total_users_data.append(users_count)
            
            # Active users in this period
            active_in_period = User.objects.filter(
                Q(userloginhistory__login_time__range=[start_date, end_date]) |
                Q(userprofile__joined_trips__end_date__gte=end_date, 
                  userprofile__joined_trips__start_date__lte=start_date)
            ).distinct().count()
            active_users_data.append(max(active_in_period, 0))
            
            # Deleted accounts up to this month
            deleted_count = User.objects.filter(
                is_active=False,
                date_joined__lte=end_date
            ).count()
            deleted_accounts_data.append(deleted_count)
            
            # Trips created up to this month
            trips_count = Trip.objects.filter(created_at__lte=end_date).count()
            total_trips_data.append(trips_count)
            
            # Completed trips up to this month
            completed_count = Trip.objects.filter(
                is_completed=True,
                created_at__lte=end_date
            ).count()
            completed_trips_data.append(completed_count)
            
            # Verified users up to this month
            verified_count = KYCProfile.objects.filter(
                status='approved',
                submitted_at__lte=end_date
            ).count()
            verified_data.append(verified_count)
            
            # Unverified users
            unverified_count = User.objects.exclude(
                kyc_profile__status='approved'
            ).filter(date_joined__lte=end_date).count()
            unverified_data.append(unverified_count)
        
        return JsonResponse({
            'success': True,
            'stats': {
                'total_users': total_users,
                'active_users': active_users,
                'deleted_accounts': deleted_accounts,
                'total_trips': total_trips,
                'completed_trips': completed_trips,
                'verified_users': verified_users,
                'non_verified_users': non_verified_users,
            },
            'chart_data': {
                'months': months,
                'total_users': total_users_data,
                'active_users': active_users_data,
                'deleted_accounts': deleted_accounts_data,
                'total_trips': total_trips_data,
                'completed_trips': completed_trips_data,
                'verified_users': verified_data,
                'unverified_users': unverified_data,
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
