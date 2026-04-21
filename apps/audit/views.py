from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.accounts.permissions import IsAdminUserRole
from .models import AuditLog
from .serializers import AuditLogSerializer


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
     Read-only API endpoint for audit logs.

    Audit logs are restricted to admin users because they may contain
    sensitive operational information.
    """

    queryset = AuditLog.objects.select_related("user").all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated, IsAdminUserRole]
    filterset_fields = ["action_type", "target_model", "created_at"]
    search_fields = ["target_model", "target_id", "description", "user__email"]
    ordering_fields = ["created_at", "action_type", "target_model"]
    ordering = ["-created_at"]


