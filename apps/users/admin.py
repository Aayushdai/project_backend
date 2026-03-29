from django.contrib import admin
from django.utils.html import format_html
from .models import UserProfile, Match, UserLoginHistory, Interest, ConstraintTag


@admin.register(Interest)
class InterestAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'user_count')
    list_filter = ('category',)
    search_fields = ('name',)

    def user_count(self, obj):
        return obj.users.count()
    user_count.short_description = "Users with this interest"


@admin.register(ConstraintTag)
class ConstraintTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'user_count')
    list_filter = ('category',)
    search_fields = ('name',)

    def user_count(self, obj):
        return obj.users.count()
    user_count.short_description = "Users with this tag"


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display  = ('user', 'full_name', 'email', 'status_badge', 'phone', 'country', 'created_at')
    list_filter   = ('status',)
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name', 'phone')
    readonly_fields = ('preview_profile_photo', 'preview_passport_photo', 'created_at')
    actions = ['approve_users', 'reject_users']
    filter_horizontal = ('interests', 'constraint_tags')

    fieldsets = (
        ('👤 Account', {
            'fields': ('user', 'status', 'rejection_reason')
        }),
        ('📸 Photos', {
            'fields': ('preview_profile_photo', 'profile_picture', 'preview_passport_photo', 'passport_photo')
        }),
        ('📋 Personal Info', {
            'fields': ('dob', 'gender', 'citizenship', 'passport_no', 'passport_expiry')
        }),
        ('📬 Contact', {
            'fields': ('phone', 'address', 'city', 'country', 'zip_code')
        }),
        ('✈️ Travel Preferences', {
            'fields': ('bio', 'location', 'travel_style', 'pace', 'accomodation_preference',
                       'budget_level', 'adventure_level', 'social_level', 'interests')
        }),
        ('🏷️ Matching Constraints', {
            'fields': ('constraint_tags', 'min_match_age', 'max_match_age'),
            'description': 'These settings ensure compatible matches. Strict tags must match for pairing.'
        }),
    )

    def full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or "—"
    full_name.short_description = "Name"

    def email(self, obj):
        return obj.user.email
    email.short_description = "Email"

    def created_at(self, obj):
        return obj.user.date_joined.strftime("%b %d, %Y")
    created_at.short_description = "Registered"

    def status_badge(self, obj):
        colors = {
            'pending':  ('#f59e0b', '⏳'),
            'approved': ('#10b981', '✅'),
            'rejected': ('#ef4444', '❌'),
        }
        color, icon = colors.get(obj.status, ('#6b7280', '?'))
        return format_html(
            '<span style="color:{};font-weight:bold">{} {}</span>',
            color, icon, obj.get_status_display()
        )
    status_badge.short_description = "Status"

    def preview_profile_photo(self, obj):
        if obj.profile_picture:
            return format_html(
                '<img src="{}" style="height:120px;width:120px;object-fit:cover;border-radius:50%;border:2px solid #ccc" />',
                obj.profile_picture.url
            )
        return "No photo uploaded"
    preview_profile_photo.short_description = "Profile Photo Preview"

    def preview_passport_photo(self, obj):
        if obj.passport_photo:
            return format_html(
                '<img src="{}" style="height:160px;max-width:280px;object-fit:cover;border-radius:8px;border:2px solid #ccc" />',
                obj.passport_photo.url
            )
        return "No passport photo uploaded"
    preview_passport_photo.short_description = "Passport Photo Preview"

    @admin.action(description="✅ Approve selected users")
    def approve_users(self, request, queryset):
        updated = queryset.update(status='approved')
        self.message_user(request, f"{updated} user(s) approved successfully.")

    @admin.action(description="❌ Reject selected users")
    def reject_users(self, request, queryset):
        updated = queryset.update(status='rejected')
        self.message_user(request, f"{updated} user(s) rejected.")


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('user1', 'user2', 'similarity_score', 'status', 'created_at')
    list_filter  = ('status',)


@admin.register(UserLoginHistory)
class UserLoginHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'login_time', 'ip_address')
    readonly_fields = ('user', 'login_time', 'ip_address', 'user_agent')