from django.contrib import admin
from .models import Booking
from apps.booking_status_history.models import BookingStatusHistory
from apps.booking_contact_log.models import BookingContactLog


class BookingStatusHistoryInline(admin.TabularInline):
    model = BookingStatusHistory
    extra = 0
    readonly_fields = ["old_status", "new_status", "changed_by", "changed_at", "comment"]

class BookingContactLogInline(admin.TabularInline):
    model = BookingContactLog
    extra = 0

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = [
        "venue",
        "booking_date",
        "start_time",
        "end_time",
        "dj",
        "status",
        "unusual_hours"
    ]
    list_filter = ["venue", "status", "unusual_hours", "booking_date"]
    search_fields = ["event_title", "notes", "dj__stage_name", "venue__name"]
    inlines = [BookingStatusHistoryInline, BookingContactLogInline]

@admin.register(BookingStatusHistory)
class BookingStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ["booking", "old_status", "new_status", "changed_by", "changed_at"]
    list_filter = ["new_status", "changed_by"]
    search_fields = ["booking__event_title", "comment"]

@admin.register(BookingContactLog)
class BookingContactLogAdmin(admin.ModelAdmin):
    list_display = ["booking", "contact_type", "outcome", "contacted_by", "contact_date"]
    list_filter = ["contact_type", "outcome", "contact_date"]
    search_fields = ["booking__event_title", "notes"]

