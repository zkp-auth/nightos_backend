from typing import Any
from django.db import transaction

from apps.audit.models import AuditLog
from  apps.bookings.models import Booking
from apps.booking_status_history.models import BookingStatusHistory
from apps.booking_contact_log.models import BookingContactLog

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