from django.contrib import admin
from django.contrib.auth.models import User
from apps.trips.models import Trip
from apps.kyc.models import KYCProfile
from django.db.models import Q
from datetime import date, timedelta
from .models import Destination
import matplotlib.pyplot as plt
import matplotlib
from io import BytesIO
import base64
import traceback
import types
from django.urls import path
from django.http import HttpResponse
from django.template.response import TemplateResponse

# Try to import from unfold first, fall back to jazzmin/django
try:
    from unfold.admin import ModelAdmin as UnfoldModelAdmin
    USING_UNFOLD = True
except ImportError:
    USING_UNFOLD = False

# Use a non-interactive backend
matplotlib.use('Agg')

def generate_chart(chart_type, labels, datasets, title, subtitle=None):
    """Generate professional-looking charts and return as base64 encoded image"""
    try:
        fig = None
        ax = None
        
        if chart_type == 'donut':
            print(f"[CHART] Generating donut chart: {title}")
            fig, ax = plt.subplots(figsize=(8, 6))
            fig.patch.set_facecolor('white')
            ax.set_facecolor('white')
            
            # Get data from both datasets
            data = [datasets[0]['data'][0], datasets[1]['data'][0]]
            colors = [datasets[0]['color'], datasets[1]['color']]
            labels_pie = [datasets[0]['label'], datasets[1]['label']]
            
            total = sum(data)
            verified_pct = int((data[0] / total) * 100) if total > 0 else 0
            
            ax.pie(data, labels=labels_pie, colors=colors, autopct='%1.0f%%', 
                   startangle=90, textprops={'color': '#333', 'fontsize': 11, 'weight': 'bold'})
            
            centre_circle = plt.Circle((0, 0), 0.70, fc='white')
            ax.add_artist(centre_circle)
            
            ax.text(0, 0, f'{verified_pct}%\nVerified', ha='center', va='center',
                   fontsize=16, weight='bold', color='#333')
            
            ax.set_title(title, fontsize=14, fontweight='bold', color='#333', pad=20)
            print(f"[CHART] Donut chart created successfully")
            
        elif chart_type == 'hbar':
            print(f"[CHART] Generating hbar chart: {title}")
            fig, ax = plt.subplots(figsize=(8, 5))
            fig.patch.set_facecolor('white')
            ax.set_facecolor('white')
            
            y_pos = [0, 1]
            values = [datasets[0]['data'][0], datasets[1]['data'][0]]
            colors = [datasets[0]['color'], datasets[1]['color']]
            labels_hbar = [datasets[0]['label'], datasets[1]['label']]
            
            bars = ax.barh(y_pos, values, color=colors, height=0.6)
            
            for bar, val in zip(bars, values):
                ax.text(val + 20, bar.get_y() + bar.get_height()/2, f'{val:,}',
                       va='center', fontsize=11, color='#333', weight='bold')
            
            ax.set_yticks(y_pos)
            ax.set_yticklabels(labels_hbar, color='#333')
            ax.set_xlim(0, max(values) * 1.15)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color('#ddd')
            ax.spines['bottom'].set_color('#ddd')
            ax.tick_params(colors='#666')
            ax.set_title(title, fontsize=14, fontweight='bold', color='#333', pad=20)
            print(f"[CHART] Hbar chart created successfully")
            
        else:  # 'bar' chart
            print(f"[CHART] Generating bar chart: {title}")
            fig, ax = plt.subplots(figsize=(10, 5))
            fig.patch.set_facecolor('white')
            ax.set_facecolor('white')
            
            x = range(len(labels))
            width = 0.35
            
            for idx, dataset in enumerate(datasets):
                offset = width * (idx - len(datasets)/2 + 0.5)
                ax.bar([i + offset for i in x], dataset['data'], width,
                      label=dataset['label'], color=dataset['color'], edgecolor='none')
            
            ax.set_xticks(x)
            ax.set_xticklabels(labels, color='#666', fontsize=9)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color('#ddd')
            ax.spines['bottom'].set_color('#ddd')
            ax.tick_params(colors='#666')
            ax.grid(True, alpha=0.15, axis='y', color='#e0e0e0')
            ax.legend(loc='upper left', framealpha=0.95, fancybox=False,
                     edgecolor='#ddd', labelcolor='#333', fontsize=9)
            ax.set_title(title, fontsize=14, fontweight='bold', color='#333', pad=20)
            print(f"[CHART] Bar chart created successfully")
        
        if fig is None or ax is None:
            print(f"[CHART ERROR] Figure or axes not created for {chart_type}")
            return None
            
        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=100, facecolor='white')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode()
        plt.close(fig)
        
        print(f"[CHART] Chart converted to base64 successfully")
        return f'data:image/png;base64,{image_base64}'
        
    except Exception as e:
        print(f"[CHART ERROR] Failed to generate {chart_type} chart: {str(e)}")
        traceback.print_exc()
        return None

# Store the original index method
_original_index = admin.AdminSite.index

def custom_index(self, request, extra_context=None):
    """Custom admin index with stats and charts"""
    try:
        print("[ADMIN] Generating stats and charts...")
        
        # Calculate stats
        thirty_days_ago = date.today() - timedelta(days=30)
        
        stats = {
            'total_users': User.objects.count(),
            'active_users': User.objects.filter(
                Q(userloginhistory__login_time__gte=thirty_days_ago) |
                Q(userprofile__joined_trips__end_date__gte=date.today())
            ).distinct().count(),
            'deleted_accounts': User.objects.filter(is_active=False).count(),
            'total_trips': Trip.objects.count(),
            'completed_trips': Trip.objects.filter(is_completed=True).count(),
            'verified_users': KYCProfile.objects.filter(status='approved').count(),
            'non_verified_users': User.objects.exclude(
                kyc_profile__status='approved'
            ).count(),
        }
        
        print(f"[ADMIN] Stats: {stats}")
        
        # Generate chart data (last 6 months)
        months = []
        total_users_data = []
        active_users_data = []
        deleted_accounts_data = []
        total_trips_data = []
        completed_trips_data = []
        verified_data = []
        unverified_data = []
        
        for i in range(5, -1, -1):
            end_date = date.today() - timedelta(days=i*30)
            start_date = end_date - timedelta(days=30)
            month_label = end_date.strftime('%b')
            months.append(month_label)
            
            users_count = User.objects.filter(date_joined__lte=end_date).count()
            total_users_data.append(users_count)
            
            active_in_period = User.objects.filter(
                Q(userloginhistory__login_time__range=[start_date, end_date]) |
                Q(userprofile__joined_trips__end_date__gte=end_date, 
                  userprofile__joined_trips__start_date__lte=start_date)
            ).distinct().count()
            active_users_data.append(max(active_in_period, 0))
            
            deleted_count = User.objects.filter(
                is_active=False,
                date_joined__lte=end_date
            ).count()
            deleted_accounts_data.append(deleted_count)
            
            trips_count = Trip.objects.filter(created_at__lte=end_date).count()
            total_trips_data.append(trips_count)
            
            completed_count = Trip.objects.filter(
                is_completed=True,
                created_at__lte=end_date
            ).count()
            completed_trips_data.append(completed_count)
            
            verified_count = KYCProfile.objects.filter(
                status='approved',
                submitted_at__lte=end_date
            ).count()
            verified_data.append(verified_count)
            
            unverified_count = User.objects.exclude(
                kyc_profile__status='approved'
            ).filter(date_joined__lte=end_date).count()
            unverified_data.append(unverified_count)
        
        print("[ADMIN] Generating chart images...")
        
        # Generate charts with professional styling
        # User Growth - Bar chart
        chart_users = generate_chart('bar', months, [
            {'label': 'Total Users', 'data': total_users_data, 'color': '#4a7ba7'},
            {'label': 'Active Users', 'data': active_users_data, 'color': '#7fbb8e'}
        ], 'USER GROWTH', 'Total vs Active Users by Month')
        
        # Trip Activity - Bar chart
        chart_trips = generate_chart('bar', months, [
            {'label': 'Created', 'data': total_trips_data, 'color': '#4a7ba7'},
            {'label': 'Completed', 'data': completed_trips_data, 'color': '#7fbb8e'}
        ], 'TRIP ACTIVITY', 'Trips created vs completed by month')
        
        # Account Verification - Donut chart
        chart_verified = generate_chart('donut', [], [
            {'label': 'Verified', 'data': [stats['verified_users']], 'color': '#7fbb8e'},
            {'label': 'Non-verified', 'data': [stats['non_verified_users']], 'color': '#e8a86b'}
        ], 'ACCOUNT VERIFICATION', 'Verified vs unverified user breakdown')
        
        # Account Status - Horizontal bar chart
        active_count = stats['total_users'] - stats['deleted_accounts']
        chart_deleted = generate_chart('hbar', [], [
            {'label': 'Active', 'data': [active_count], 'color': '#4a7ba7'},
            {'label': 'Deleted', 'data': [stats['deleted_accounts']], 'color': '#e53e3e'}
        ], 'ACCOUNT STATUS', 'Active vs deleted account distribution')
        
        print("[ADMIN] Charts created, adding to context...")
        
        extra_context = extra_context or {}
        extra_context['stats'] = stats
        extra_context['chart_users'] = chart_users
        extra_context['chart_trips'] = chart_trips
        extra_context['chart_verified'] = chart_verified
        extra_context['chart_deleted'] = chart_deleted
        
        print("[ADMIN] Context ready, calling original index...")
        
    except Exception as e:
        print(f"[ADMIN ERROR] {e}")
        traceback.print_exc()
        extra_context = extra_context or {}
    
    # Call the original index
    return _original_index(self, request, extra_context)

# Patch the admin site's index method
admin.AdminSite.index = custom_index

# Customize header
admin.site.site_header = "TCS Admin"
admin.site.site_title = "TCS Admin"
admin.site.index_title = "Welcome to TCS Admin"


class DestinationAdmin(admin.ModelAdmin):
    list_display = ("name", "country", "description")
    search_fields = ("name", "country")
    list_filter = ("country",)
    ordering = ("name",)

# Register the model
admin.site.register(Destination, DestinationAdmin)


def patch_admin_site():
    """Called from urls.py after all apps are loaded"""
    print("[PATCH] Admin site patched!")
    pass

# Create custom view for visual page
_original_get_urls = admin.site.get_urls

def custom_get_urls(self=None):
    """Add custom visual view URL"""
    # Get the original URLs (handle both bound and unbound calls)
    if self is None:
        self = admin.site
    urls = _original_get_urls()
    custom_urls = [
        path('visual/', admin_site_visual, name='admin_visual'),
    ]
    return custom_urls + urls

# Define the visual view
def admin_site_visual(request):
    """Display visual graphs page"""
    if not request.user.is_staff:
        return HttpResponse("Unauthorized", status=403)
    
    try:
        print("[VISUAL] Generating stats and charts for visual page...")
        
        # Calculate stats
        thirty_days_ago = date.today() - timedelta(days=30)
        
        stats = {
            'total_users': User.objects.count(),
            'active_users': User.objects.filter(
                Q(userloginhistory__login_time__gte=thirty_days_ago) |
                Q(userprofile__joined_trips__end_date__gte=date.today())
            ).distinct().count(),
            'deleted_accounts': User.objects.filter(is_active=False).count(),
            'total_trips': Trip.objects.count(),
            'completed_trips': Trip.objects.filter(is_completed=True).count(),
            'verified_users': KYCProfile.objects.filter(status='approved').count(),
            'non_verified_users': User.objects.exclude(
                kyc_profile__status='approved'
            ).count(),
        }
        
        print(f"[VISUAL] Stats: {stats}")
        
        # Generate chart data (last 6 months)
        months = []
        total_users_data = []
        active_users_data = []
        deleted_accounts_data = []
        total_trips_data = []
        completed_trips_data = []
        verified_data = []
        unverified_data = []
        
        for i in range(5, -1, -1):
            end_date = date.today() - timedelta(days=i*30)
            start_date = end_date - timedelta(days=30)
            month_label = end_date.strftime('%b')
            months.append(month_label)
            
            users_count = User.objects.filter(date_joined__lte=end_date).count()
            total_users_data.append(users_count)
            
            active_in_period = User.objects.filter(
                Q(userloginhistory__login_time__range=[start_date, end_date]) |
                Q(userprofile__joined_trips__end_date__gte=end_date, 
                  userprofile__joined_trips__start_date__lte=start_date)
            ).distinct().count()
            active_users_data.append(max(active_in_period, 0))
            
            deleted_count = User.objects.filter(
                is_active=False,
                date_joined__lte=end_date
            ).count()
            deleted_accounts_data.append(deleted_count)
            
            trips_count = Trip.objects.filter(created_at__lte=end_date).count()
            total_trips_data.append(trips_count)
            
            completed_count = Trip.objects.filter(
                is_completed=True,
                created_at__lte=end_date
            ).count()
            completed_trips_data.append(completed_count)
            
            verified_count = KYCProfile.objects.filter(
                status='approved',
                submitted_at__lte=end_date
            ).count()
            verified_data.append(verified_count)
            
            unverified_count = User.objects.exclude(
                kyc_profile__status='approved'
            ).filter(date_joined__lte=end_date).count()
            unverified_data.append(unverified_count)
        
        print("[VISUAL] Generating chart images...")
        
        # Generate charts with professional styling
        # User Growth - Bar chart
        chart_users = generate_chart('bar', months, [
            {'label': 'Total Users', 'data': total_users_data, 'color': '#4a7ba7'},
            {'label': 'Active Users', 'data': active_users_data, 'color': '#7fbb8e'}
        ], 'USER GROWTH', 'Total vs Active Users by Month')
        
        # Trip Activity - Bar chart
        chart_trips = generate_chart('bar', months, [
            {'label': 'Created', 'data': total_trips_data, 'color': '#4a7ba7'},
            {'label': 'Completed', 'data': completed_trips_data, 'color': '#7fbb8e'}
        ], 'TRIP ACTIVITY', 'Trips created vs completed by month')
        
        # Account Verification - Donut chart
        chart_verified = generate_chart('donut', [], [
            {'label': 'Verified', 'data': [stats['verified_users']], 'color': '#7fbb8e'},
            {'label': 'Non-verified', 'data': [stats['non_verified_users']], 'color': '#e8a86b'}
        ], 'ACCOUNT VERIFICATION', 'Verified vs unverified user breakdown')
        
        # Account Status - Horizontal bar chart
        active_count = stats['total_users'] - stats['deleted_accounts']
        chart_deleted = generate_chart('hbar', [], [
            {'label': 'Active', 'data': [active_count], 'color': '#4a7ba7'},
            {'label': 'Deleted', 'data': [stats['deleted_accounts']], 'color': '#e53e3e'}
        ], 'ACCOUNT STATUS', 'Active vs deleted account distribution')
        
        print("[VISUAL] Charts created, preparing response...")
        
        context = {
            'stats': stats,
            'chart_users': chart_users,
            'chart_trips': chart_trips,
            'chart_verified': chart_verified,
            'chart_deleted': chart_deleted,
            'title': 'Visual Analytics',
            'app_list': admin.site.get_app_list(request),
            'has_permission': True,
        }
        
        return TemplateResponse(request, 'admin/visual.html', context)
        
    except Exception as e:
        print(f"[VISUAL ERROR] {e}")
        traceback.print_exc()
        return TemplateResponse(request, 'admin/visual.html', {'error': str(e)})

# Patch the global admin.site instance
admin.site.get_urls = types.MethodType(lambda self: custom_get_urls(self), admin.site)
admin.site.admin_site_visual = admin_site_visual

# Store the original get_app_list method
_original_get_app_list = admin.site.get_app_list

def get_app_list_with_visual(self, request):
    """Add Visual to the app list"""
    app_list = _original_get_app_list(request)
    
    # Create Visual section
    visual_section = {
        'name': 'Visual',
        'app_label': 'visual',
        'app_url': '/admin/visual/',
        'has_module_perms': True,
        'models': [
            {
                'name': 'Graph and chart',
                'object_name': 'GraphChart',
                'admin_url': '/admin/visual/',
                'add_url': None,
                'change_url': '/admin/visual/',
                'view_only': True,
            }
        ]
    }
    
    # Insert at the very beginning
    app_list.insert(0, visual_section)
    
    return app_list

# Patch the global admin.site instance with bound method
admin.site.get_app_list = types.MethodType(get_app_list_with_visual, admin.site)

