from django.db import models
from django.conf import settings

from apps.common.models import TimeStampedModel

class AuditLog(TimeStampedModel):
    """
    Stores important user actions across the platform.

    This model provides traceability and accountability for sensitive
    operations such as creating, updating, deleting, or changing the
    status of key business entities like bookings and DJs.
    """

    class ActionTypes(models.TextChoices):
        CREATE = "create", "Create"
        UPDATE = "update", "Update"
        DELETE = "delete", "Delete"
        STATUS_CHANGE = "status_change", "Status Change"
        LOGIN = "login", "Login",
        FAILED_LOGIN = "failed_login", "Failed Login"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="audit_logs",
        help_text="User responsible for the action, if available."
    )
    action_type = models.CharField(
        max_length=30,
        choices=ActionTypes.choices,
        help_text="Type of action performed by the user."
    )
    target_model = models.CharField(
        max_length=100,
        help_text="Name of the model affected by the action (e.g., Booking, DJ, Venue)."
    )
    target_id = models.CharField(
        max_length=50,
        blank=True,
        help_text="Identifier of the affected record."
    )
    description = models.TextField(
        blank=True,
        help_text="Humaan-readable description of the action."
    )
    old_data = models.JSONField(
        blank=True,
        null=True,
        help_text="Optional Snapshot of the relevant data before the change."
    )
    new_data = models.JSONField(
        blank=True,
        null=True,
        help_text="Optional Snapshot of the relevant data after the change."
    )
    ip_address = models.GenericIPAddressField(
        blank=True,
        null=True,
        help_text="IP address from which the action was performed, if available."
    )

    class Meta:
        db_table = "audit_log"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["action_type"]),
            models.Index(fields=["target_model"]),
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self):
        return f"{self.action_type} on {self.target_model} by {self.user or 'System'}"





