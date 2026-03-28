from django.contrib import admin
from .models import KYCProfile


@admin.register(KYCProfile)
class KYCProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'status', 'submitted_at', 'reviewed_at']
    list_filter = ['status', 'nationality', 'city']
    search_fields = ['user__email', 'user__username', 'full_name', 'id_number']
    readonly_fields = ['submitted_at', 'reviewed_at']