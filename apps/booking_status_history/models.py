from django.db import models

from apps.bookings.models import Booking
from django.conf import settings


class BookingStatusHistory(models.Model):
    """
    Stores the history of booking status changes.

    This helps track the operational flow over time and provides
    accountability for confirmation-related changes.
    """
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name="status_history",
        help_text="The booking associated with this status change."
    )
    old_status = models.CharField(
        max_length=40,
        blank=True,
        help_text="Previous status of the booking before the change."
    )
    new_status = models.CharField(
        max_length=40,
        help_text="New status of the booking after the change."
    )
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text="User who changed this status history."
    )
    comment = models.TextField(
        blank=True,
        help_text="Optional comment about the status change, such as reasons for cancellation or notes on confirmation."
    )
    changed_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Date and time when the status was changed."
    )
    class Meta:
        db_table = "booking_status_history"
        ordering = ["-changed_at"]

    def __str__(self):
        return f"{self.booking.id} - {self.old_status} - {self.new_status}"

