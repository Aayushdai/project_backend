from django.contrib import admin
from .models import Trip, City, ItineraryItem, Destination, TripExpenseBudget, TripReview, TripPhoto


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'country')
    search_fields = ('name',)


@admin.register(ItineraryItem)
class ItineraryItemAdmin(admin.ModelAdmin):
    list_display = ("trip", "day", "activity", "notes")
    search_fields = ("activity", "trip__title")


@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'city', 'get_country')
    list_filter = ('city',)
    search_fields = ('name', 'city__name', 'city__country')
    fields = ('name', 'description', 'location', 'city', 'image')

    def get_country(self, obj):
        return obj.city.country

    get_country.short_description = 'Country'


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ("title", "creator", "destination", "start_date", "end_date")
    search_fields = ("title", "creator__username")
    list_filter = ("destination", "start_date")
    ordering = ("-start_date",)


@admin.register(TripExpenseBudget)
class TripExpenseBudgetAdmin(admin.ModelAdmin):
    list_display = ("trip", "category", "amount", "created_at")
    search_fields = ("trip__title", "category")
    list_filter = ("trip", "created_at")
    ordering = ("-created_at",)


@admin.register(TripReview)
class TripReviewAdmin(admin.ModelAdmin):
    list_display = ("trip", "reviewer", "rating", "created_at")
    search_fields = ("trip__title", "reviewer__user__username")
    list_filter = ("trip", "rating", "created_at")
    ordering = ("-created_at",)


@admin.register(TripPhoto)
class TripPhotoAdmin(admin.ModelAdmin):
    list_display = ("trip", "uploaded_by", "created_at")
    search_fields = ("trip__title", "uploaded_by__user__username")
    list_filter = ("trip", "created_at")
    ordering = ("-created_at",)