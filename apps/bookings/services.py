from typing import Any
from django.db import transaction
from datetime import datetime, timedelta

from apps.audit.models import AuditLog
from  apps.bookings.models import Booking
from apps.booking_status_history.models import BookingStatusHistory
from apps.booking_contact_log.models import BookingContactLog
from apps.bookings.exceptions import BookingConflictError

def _build_booking_interval(booking_date, start_time, end_time):
    """
    Build normalized datetime boundaries for a booking interval.

    If end_time is earlier than or equal to start_time, we assume
    the booking crosses midnight into the next day.
    """
    if start_time is None or end_time is None:
        return None, None

    start_dt = datetime.combine(booking_date, start_time)
    end_dt = datetime.combine(booking_date, end_time)

    if end_dt <= start_dt:
        end_dt += timedelta(days=1)

    return start_dt, end_dt

def _intervals_overlap(start_a, end_a, start_b, end_b):
    """
    Return True if two datetime intervals overlap.
    """
    return start_a < end_b and start_b < end_a

def validate_booking_conflicts(
        *,
        venue,
        booking_date,
        start_time=None,
        end_time=None,
        dj=None,
        exclude_booking_id=None,
):
    """
    Validate that a booking does not conflict with existing venue or DJ bookings.

    Rules:
    - A venue cannot have overlapping bookings at the same time.
    - A DJ cannot be assigned to overlapping bookings at the same time.
    Bookings without a full time range are skipped from overlap checking for now.
    """
    if venue is None:
        raise ValueError("A venue is required for conflict validation.")

    # If one or both times are missing, skip overlap validation for MVP.
    # The system can still track the booking, but conflict precision is limited.
    if start_time is None and end_time is None:
        return

    new_start, new_end = _build_booking_interval(booking_date, start_time, end_time)

    existing_bookings = Booking.objects.filter(
        booking_date=booking_date,
    ).exclude(status=Booking.Status.CANCELLED)

    if exclude_booking_id is not None:
        existing_bookings = existing_bookings.exclude(id=exclude_booking_id)

    # Venue conflict check
    venue_bookings = existing_bookings.filter(venue=venue)

    for existing in venue_bookings:
        if existing.start_time is None or existing.end_time is None:
            continue

        existing_start, existing_end = _build_booking_interval(
            existing.booking_date,
            existing.start_time,
            existing.end_time
        )

        if _intervals_overlap(new_start, new_end, existing_start, existing_end):
            raise BookingConflictError(
                f"Venue conflict detected: '{venue.name}' already has a booking"
                f"overlapping {booking_date} {start_time}-{end_time}."
            )

    # DJ conflict check
    if dj is not None:
        dj_bookings = Booking.objects.filter(dj=dj)

        for existing in dj_bookings:
            if existing.start_time is None or existing.end_time is None:
                continue

            existing_start, existing_end = _build_booking_interval(
                existing.booking_date,
                existing.start_time,
                existing.end_time,
            )

            if _intervals_overlap(new_start, new_end, existing_start, existing_end):
                dj_name = existing.dj.stage_name if existing.dj else "Selected DJ"
                raise BookingConflictError(
                    f"DJ conflict detected: '{dj_name}' is already booked for an overlapping time slot."
                )





def create_audit_log(
        *,
        user=None,
        action_type: str,
        target_model: str,
        target_id: str = "",
        description: str = "",
        old_data: dict | None = None,
        new_data: dict | None = None,
        ip_address: str | None = None,
) -> AuditLog:
    """
    Create a system audit log entry.

    This helper centralizes audit logging so business actions
    can record traceable events in a consistent way.
    """
    return AuditLog.objects.create(
        user=user,
        action_type=action_type,
        target_model=target_model,
        target_id=target_id,
        description=description,
        old_data=old_data,
        new_data=new_data,
        ip_address=ip_address
    )

@transaction.atomic
def create_booking(
        *,
        venue,
        booking_date,
        start_time=None,
        end_time=None,
        dj=None,
        event_title: str = "",
        status: str = Booking.Status.TO_BOOK,
        notes: str = "",
        unusual_hours: bool = False,
        created_by=None,
        ip_address: str | None = None,

) -> Booking:
    """
    Create a new booking and automatically register an audit log.

    The transaction ensures the booking and its audit entry are saved together.
    """

    if venue is None:
        raise ValueError("Venue is required to create a booking.")
    if booking_date is None:
        raise ValueError("Booking date is required to create a booking.")

    validate_booking_conflicts(
        venue=venue,
        booking_date=booking_date,
        start_time=start_time,
        end_time=end_time,
        dj=dj,
    )

    booking = Booking.objects.create(
        venue=venue,
        booking_date=booking_date,
        start_time=start_time,
        end_time=end_time,
        dj=dj,
        event_title=event_title,
        status=status,
        notes=notes,
        unusual_hours=unusual_hours,
        created_by=created_by,
        updated_by=created_by
    )

    create_audit_log(
        user=created_by,
        action_type=AuditLog.ActionTypes.CREATE,
        target_model="Booking",
        target_id=str(booking.id),
        description="Booking created successfully.",
        new_data={
            "venue": booking.venue.name,
            "booking_date": str(booking.booking_date),
            "status": booking.status,
            "dj": booking.dj.stage_name if booking.dj else None,
        },
        ip_address=ip_address,
    )

    return booking

@transaction.atomic
def update_booking(
        *,
        booking: Booking,
        updated_by=None,
        ip_address: str | None = None,
        **fields: Any,
) -> Booking:
    """
    Update booking fields and register an audit log.

    Only provided fields are updated. Old and new values are captured
    for traceability in the audit log.
    """
    old_data = {}
    new_data = {}

    # Determine the final values after update, even if some fields are omitted.
    final_venue = fields.get("venue", booking.venue)
    final_booking_date = fields.get("booking_date", booking.booking_date)
    final_start_time = fields.get("start_time", booking.start_time)
    final_end_time = fields.get("end_time", booking.end_time)
    final_dj = fields.get("dj", booking.dj)

    validate_booking_conflicts(
        venue=final_venue,
        booking_date=final_booking_date,
        start_time=final_start_time,
        end_time=final_end_time,
        dj=final_dj,
        exclude_booking_id=booking.id,
    )

    for field_name, new_value in fields.items():
        old_value = getattr(booking, field_name)
        old_data[field_name] = str(old_value) if old_value is not None else None
        new_data[field_name] = str(new_value) if new_value is not None else None
        setattr(booking, field_name, new_value)

    booking.updated_by = updated_by
    booking.save()

    create_audit_log(
        user=updated_by,
        action_type=AuditLog.ActionTypes.UPDATE,
        target_model="Booking",
        target_id=str(booking.id),
        description="Booking updated successfully.",
        old_data=old_data,
        new_data=new_data,
        ip_address=ip_address,
    )

    return booking

@transaction.atomic
def change_booking_status(
        *,
        booking: Booking,
        new_status: str,
        changed_by=None,
        comment: str = "",
        ip_address: str | None = None,
) -> Booking:
    """
    Change the status of a booking and create both status history
    and audit log records.

    If the status is unchanged, the function returns the booking
    without creating extra records.
    """
    old_status = booking.status

    if old_status == new_status:
        return booking

    booking.status = new_status
    booking.updated_by = changed_by
    booking.save()

    BookingStatusHistory.objects.create(
        booking=booking,
        old_status=old_status,
        new_status=new_status,
        changed_by=changed_by,
        comment=comment
    )

    create_audit_log(
        user=changed_by,
        action_type=AuditLog.ActionTypes.STATUS_CHANGE,
        target_model="Booking",
        target_id=str(booking.id),
        description=f"Booking status changed from '{old_status}' to '{new_status}'.",
        old_data={"status": old_status},
        new_data={"status": new_status, "comment": comment},
        ip_address=ip_address,
    )
    return booking


@transaction.atomic
def create_booking_contact_log(
        *,
        booking: Booking,
        contact_type: str,
        outcome: str,
        contact_date,
        contacted_by=None,
        notes: str = "",
        ip_address: str | None = None,
) -> BookingContactLog:
    """
    Create a communication log entry for a booking and register an audit log.

    This is especially useful for WhatsApp-based follow-up workflows.
    """
    contact_log = BookingContactLog.objects.create(
        booking=booking,
        contact_type=contact_type,
        outcome=outcome,
        contact_date=contact_date,
        contacted_by=contacted_by,
        notes=notes
    )

    create_audit_log(
        user=contacted_by,
        action_type=AuditLog.ActionTypes.UPDATE,
        target_model="BookingContactLog",
        target_id=str(contact_log.id),
        description=f"Booking contact log created successfully.",
        new_data={
            "booking_id": booking.id,
            "contact_type": contact_type,
            "outcome": outcome,
            "contact_date": str(contact_date),
        },
        ip_address=ip_address,
    )

    return contact_log

@transaction.atomic
def delete_booking(
        *,
        booking: Booking,
        deleted_by=None,
        ip_address: str | None = None,
) -> None:
    """
    Delete a booking and register an audit log.

    The audit log captures the state of the booking before deletion for traceability.
    """
    old_data = {
        "venue": booking.venue.name,
        "booking_date": str(booking.booking_date),
        "status": booking.status,
        "dj": booking.dj.stage_name if booking.dj else None,
    }

    booking.delete()

    create_audit_log(
        user=deleted_by,
        action_type=AuditLog.ActionTypes.DELETE,
        target_model="Booking",
        target_id=str(booking.id),
        description="Booking deleted successfully.",
        old_data=old_data,
        ip_address=ip_address,
    )