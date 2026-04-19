from django.contrib import admin
from .models import DJ, Genre


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    """Admin configuration for the Genre model"""
    list_display = ["name", "slug", "created_at"]
    search_fields = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}

@admin.register(DJ)
class DJAdmin(admin.ModelAdmin):
    """Admin configuration for the DJ model"""
    list_display = ["stage_name", "full_name", "phone", "is_active", "created_at"]
    search_fields = ["stage_name", "full_name", "phone", "email"]
    list_filter = ["is_active", "genres"]
    filter_horizontal = ["genres"]
    
