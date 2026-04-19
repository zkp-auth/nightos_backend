from django.contrib import admin
from .models import Venue


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    """
    Admin configuration for venue management
    """

    list_display = ["name", "city", "slug", "created_at"]
    search_fields = ["name", "city", "slug"]
    prepopulated_fields = {"slug": ("name",)}

