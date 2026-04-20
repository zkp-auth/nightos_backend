from django.contrib import admin
from .models import AuditLog

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Admin configuration for the AuditLog model"""

    list_display = ["action_type", "target_model", "target_id", "user", "created_at"]
    list_filter = ["action_type", "target_model", "created_at"]
    search_fields = ["target_model", "target_id", "description", "user__email"]
    readonly_fields = [
        "user",
        "action_type",
        "target_model",
        "target_id",
        "description",
        "old_data",
        "new_data",
        "ip_address",
        "created_at",
        "updated_at",
    ]
    def has_add_permission(self, request):
        # Audit logs should be created by the system, not manually in admin.
        return False

    def has_change_permission(self, request, obj=None):
        # Audit logs should not be editable one created.
        return False

