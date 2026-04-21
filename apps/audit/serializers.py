from rest_framework import serializers

from .models import AuditLog

class AuditLogSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for audit logs.
    """

    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = AuditLog
        fields = [
            "id",
            "user",
            "user_email",
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
        read_only_fields = fields