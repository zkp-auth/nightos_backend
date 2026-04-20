from django.db import models

from apps.bookings.models import Booking
from django.conf import settings


class BookingContactLog(models.Model):
    """
    Tracks communication attempts related to a booking.

    This prepares the system for WhatsApp-based follow-up workflows
    and later notification automation.
    """
    class ContactType(models.TextChoices):
        WHATSAPP = "whatsapp", "WhatsApp"
        EMAIL = "email", "Email"
        SMS = "sms", "SMS"
        PHONE = "phone", "Phone"
        Others = "others", "Others"

    class Outcome(models.TextChoices):
        SENT = "sent", "Sent"
        REPLIED = "replied", "Replied"
        NO_RESPONSE = "no_response", "No Response"
        CONFIRMED = "confirmed", "Confirmed"
        DECLINED = "declined", "Declined"
        FOLLOW_UP_NEEDED = "follow_up_needed", "Follow-up Needed"

    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name="contact_logs",
        help_text="Booking related to the communication attempt."
    )
    contact_type = models.CharField(
        max_length=20,
        choices=ContactType.choices,
        default=ContactType.WHATSAPP,
        help_text="Method of contact used for this communication attempt."
    )
    contacted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text="User who contacted the DJ or client."
    )
    contact_date = models.DateField(
        help_text="Date when the contact attempt was made."
    )
    outcome = models.CharField(
        max_length=30,
        choices=Outcome.choices,
        help_text="Result of the communication attempt."
    )
    notes = models.TextField(
        blank=True,
        help_text="Additional notes about the contact attempt, such as details of the conversation or next steps."
    )
    contacted_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Date and time when the contact log entry was recorded."
    )
    class Meta:
        db_table = "booking_contact_logs"
        ordering = ["-contact_date"]
