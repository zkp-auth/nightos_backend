from django.db import models
from django.conf import settings

from apps.common.models import TimeStampedModel
from apps.djs.models import DJ
from apps.venues.models import Venue


class Booking(TimeStampedModel):
    """
    Represents a DJ booking for a specific venue and date.

    A booking may start as an empty operational slot and later be assigned
    to a DJ. Status tracking is used to reflect the real-world workflow
    of confirmations and booking updates.
    """

    class Status(models.TextChoices):
        TO_BOOK = "to_book", "To Book"
        PENDING_DJ_CONFIRMATION = "pending_dj_confirmation", "Pending DJ Confirmation"
        PENDING_CLIENT_CONFIRMATION = "pending_client_confirmation", "Pending Client Confirmation"
        CONFIRMED = "confirmed", "Confirmed"
        VALIDATED_CHANGE = "validated_change", "Validated Change"
        UNUSUAL_SCHEDULE = "unusual_schedule", "Unusual Schedule"
        CANCELLED = "cancelled", "Cancelled"

    venue = models.ForeignKey(
        Venue,
        on_delete=models.CASCADE,
        related_name="bookings",
        help_text="Venue where the booking take place.",
    )
    booking_date = models.DateField(
        help_text="Date of the booking.",
    )
    start_time = models.TimeField(
        blank=True,
        null=True,
        help_text="Scheduled start time for the booking.",
    )
    end_time = models.TimeField(
        blank=True,
        null=True,
        help_text="Scheduled end time for the booking.",
    )
    dj = models.ForeignKey(
        DJ,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="bookings",
        help_text="Assigned DJ. Can be empty while the slot is still open.",
    )
    event_title = models.CharField(
        max_length=200,
        blank=True,
        help_text="Optional title or description of the event.",
    )
    status = models.CharField(
        max_length=40,
        choices=Status.choices,
        default=Status.TO_BOOK,
        help_text="Operational booking status used in the confirmation workflow.",
    )
    notes = models.TextField(
        blank=True,
        help_text="Internal notes about the booking, such as client preferences or special instructions.",
    )
    unusual_hours = models.BooleanField(
        default=False,
        help_text="Marks bookings with unusual or exceptional schedule hours.",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="created_bookings",
        help_text="User who created the booking.",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="updated_bookings",
        help_text="User who last updated the booking.",
    )

    class Meta:
        db_table = "bookings"
        ordering = ["booking_date", "start_time"]
        indexes = [
            models.Index(fields=["booking_date"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        dj_name = self.dj.stage_name if self.dj else "Unassigned"
        return f"{self.venue.name} - {self.booking_date} - {dj_name}"
        # return f"{self.booking_date} - {dj_name} at {self.venue.name}"


