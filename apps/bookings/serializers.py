from django.contrib.auth import user_logged_in
from rest_framework import serializers
from .models import Booking
from apps.booking_contact_log.models import BookingContactLog
from apps.booking_status_history.models import BookingStatusHistory
from apps.bookings.services import (
    change_booking_status,
    create_booking,
    create_booking_contact_log,
    update_booking
)
from apps.djs.models import DJ
from apps.djs.serializers import DJSerializer
from apps.venues.models import Venue
from apps.venues.serializers import VenueSerializer

class BookingSerializer(serializers.ModelSerializer):
    """
    Read serializer for bookings.

    Includes nested venue and DJ details for frontend convenience.
    """
    venue = VenueSerializer(read_only=True)
    dj = DJSerializer(read_only=True)
    created_by_email = serializers.EmailField(source="created_by.email", read_only=True)
    updated_by_email = serializers.EmailField(source="updated_by.email", read_only=True)

    class Meta:
        model = Booking
        fields =[
            "id",
            "venue",
            "booking_date",
            "start_time",
            "end_time",
            "dj",
            "event_title",
            "status",
            "notes",
            "unusual_hours",
            "created_by",
            "created_by_email",
            "updated_by",
            "updated_by_email",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

class CreateBookingSerializer(serializers.Serializer):
    """
    Input serializer for creating bookings.

    Business logic is handled in the service layer to ensure audit logs are created.
    """
    venue = serializers.PrimaryKeyRelatedField(queryset=Venue.objects.all())
    booking_date = serializers.DateField()
    start_time = serializers.TimeField(required=False, allow_null=True)
    end_time = serializers.TimeField(required=False, allow_null=True)
    dj = serializers.PrimaryKeyRelatedField(queryset=DJ.objects.all(), required=False, allow_null=True)
    event_title = serializers.CharField(required=False, allow_blank=True, max_length=200)
    status = serializers.ChoiceField(
        choices=Booking.Status.choices,
        required=False,
        default=Booking.Status.TO_BOOK
    )
    notes = serializers.CharField(required=False, allow_blank=True)
    unusual_hours = serializers.BooleanField(required=False, default=False)

    def validate(self, attrs):
        """
        Basic serializer-level validation.

        We keep business workflow logic in the service layer, but format
        and obvious inconsistencies should be handled here.
        """
        start_time = attrs.get("start_time")
        end_time = attrs.get("end_time")

        # Nightlife schedules may cross midnight, so we do not force end_time > start_time.
        # We only validate when one time is provided without the other and the workflow requires both.
        if start_time and not end_time:
            raise serializers.ValidationError("End time is required when start time is provided.")
        return attrs

    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user if request else None
        ipaddress = self._get_client_ip()

        return create_booking(
            venue=validated_data["venue"],
            booking_date=validated_data["booking_date"],
            start_time=validated_data.get("start_time"),
            end_time=validated_data.get("end_time"),
            dj=validated_data.get("dj"),
            event_title=validated_data.get("event_title", ""),
            status=validated_data.get("status", Booking.Status.TO_BOOK),
            notes=validated_data.get("notes", ""),
            unusual_hours=validated_data.get("unusual_hours", False),
            created_by=user,
            ip_address=ipaddress,
        )

    def _get_client_ip(self):
        request = self.context.get("request")
        if not request:
            return None
        forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")

class UpdateBookingSerializer(serializers.Serializer):
    """
    Input serializer for updating bookings.

    Use the service layer to keep business logic centralized.
    """
    venue = serializers.PrimaryKeyRelatedField(queryset=Venue.objects.all())
    booking_date = serializers.DateField(required=False)
    start_time = serializers.TimeField(required=False, allow_null=True)
    end_time = serializers.TimeField(required=False, allow_null=True)
    dj = serializers.PrimaryKeyRelatedField(queryset=DJ.objects.all(), required=False, allow_null=True)
    event_title = serializers.CharField(required=False, allow_blank=True, max_length=200)
    status = serializers.ChoiceField(choices=Booking.Status.choices, required=False)
    notes = serializers.CharField(required=False, allow_blank=True)
    unusual_hours = serializers.BooleanField(required=False)

    def create(self, instance, validated_data):
        request = self.context.get("request")
        user = request.user if request else None
        ipaddress = self._get_client_ip()

        return update_booking(
            booking=instance,
            updated_by=user,
            ip_address=ipaddress,
            **validated_data
        )

    def _get_client_ip(self):
        request = self.context.get("request")
        if not request:
            return None
        forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")

class ChangeBookingStatusSerializer(serializers.Serializer):
    """
    Input serializer for updating booking status.

    The actual status transition logic is handled in the service layer
    to ensure audit logs and status history are properly maintained.
    """
    new_status = serializers.ChoiceField(choices=Booking.Status.choices, required=False)
    comment = serializers.CharField(required=False, allow_blank=True)

    def save(self, **kwargs):
        booking = self.context["booking"]
        request = self.context.get("request")
        user = request.user if request else None
        ipaddress = self._get_client_ip()

        return change_booking_status(
            booking=booking,
            new_status=self.validated_data.get("new_status"),
            changed_by=user,
            comment=self.validated_data.get("comment", ""),
            ip_address=ipaddress,
        )

    def _get_client_ip(self):
        request = self.context.get("request")
        if not request:
            return None
        forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")

class BookingStatusHistorySerializer(serializers.ModelSerializer):
    """
    Read serializer for booking status history.
    """
    changed_by_email = serializers.EmailField(source="changed_by.email", read_only=True)

    class Meta:
        model = BookingStatusHistory
        fields = [
            "id",
            "booking",
            "old_status",
            "new_status",
            "changed_by",
            "changed_by_email",
            "comment",
            "changed_at",
        ]
        read_only_fields = fields

class BookingContactLogSerializer(serializers.ModelSerializer):
    """
    Read serializer for booking contact logs.
    """
    contacted_by_email = serializers.EmailField(source="contacted_by.email", read_only=True)

    class Meta:
        model = BookingContactLog
        fields = [
            "id",
            "booking",
            "contact_type",
            "contacted_by",
            "contacted_by_email",
            "contact_date",
            "outcome",
            "notes",
            "created_at",
        ]
        read_only_fields = fields

class CreateBookingContactLogSerializer(serializers.Serializer):
    """
    Input serializer for creating a booking contact log.
    """
    contact_type = serializers.ChoiceField(choices=BookingContactLog.ContactType.choices)
    contact_date = serializers.DateTimeField()
    outcome = serializers.ChoiceField(choices=BookingContactLog.Outcome.choices)
    notes = serializers.CharField(required=False, allow_blank=True)

    def save(self, **kwargs):
        booking = self.context["booking"]
        request = self.context.get("request")
        user = request.user if request else None
        ipaddress = self._get_client_ip()

        return create_booking_contact_log(
            booking=booking,
            contact_type=self.validated_data["contact_type"],
            outcome=self.validated_data["outcome"],
            contact_date=self.validated_data["contact_date"],
            contacted_by=user,
            notes=self.validated_data.get("notes", ""),
            ip_address=ipaddress,
        )

    def _get_client_ip(self):
        request = self.context.get("request")
        if not request:
            return None
        forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")





