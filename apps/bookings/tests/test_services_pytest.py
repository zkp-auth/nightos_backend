import pytest
from datetime import date, time

from django.utils import timezone

from apps.audit.models import AuditLog
from apps.bookings.exceptions import BookingConflictError
from apps.bookings.models import Booking
from apps.booking_contact_log.models import BookingContactLog
from apps.booking_status_history.models import BookingStatusHistory
from apps.bookings.services import (
    change_booking_status,
    create_booking,
    create_booking_contact_log,
    update_booking,
)


@pytest.mark.django_db
def test_create_booking_successfully(user, venue, dj):
    booking = create_booking(
        venue=venue,
        booking_date=date(2026, 4, 25),
        start_time=time(22, 0),
        end_time=time(2, 0),
        dj=dj,
        event_title="Saturday Night Party",
        created_by=user,
    )

    assert booking.id is not None
    assert booking.venue == venue
    assert booking.dj == dj
    assert booking.status == Booking.Status.TO_BOOK
    assert Booking.objects.count() == 1
    assert AuditLog.objects.count() == 1


@pytest.mark.django_db
def test_prevent_overlapping_booking_for_same_venue(user, venue, dj, second_dj):
    create_booking(
        venue=venue,
        booking_date=date(2026, 4, 25),
        start_time=time(22, 0),
        end_time=time(2, 0),
        dj=dj,
        event_title="Main Saturday Event",
        created_by=user,
    )

    with pytest.raises(BookingConflictError):
        create_booking(
            venue=venue,
            booking_date=date(2026, 4, 25),
            start_time=time(23, 0),
            end_time=time(1, 0),
            dj=second_dj,
            event_title="Conflicting Venue Event",
            created_by=user,
        )

    assert Booking.objects.count() == 1


@pytest.mark.django_db
def test_prevent_overlapping_booking_for_same_dj(user, venue, second_venue, dj):
    create_booking(
        venue=venue,
        booking_date=date(2026, 4, 25),
        start_time=time(22, 0),
        end_time=time(2, 0),
        dj=dj,
        event_title="Venue One Event",
        created_by=user,
    )

    with pytest.raises(BookingConflictError):
        create_booking(
            venue=second_venue,
            booking_date=date(2026, 4, 25),
            start_time=time(23, 30),
            end_time=time(1, 30),
            dj=dj,
            event_title="Conflicting DJ Event",
            created_by=user,
        )

    assert Booking.objects.count() == 1


@pytest.mark.django_db
def test_allow_non_overlapping_bookings_for_same_venue(user, venue, dj, second_dj):
    create_booking(
        venue=venue,
        booking_date=date(2026, 4, 25),
        start_time=time(18, 0),
        end_time=time(21, 0),
        dj=dj,
        event_title="Early Event",
        created_by=user,
    )

    second_booking = create_booking(
        venue=venue,
        booking_date=date(2026, 4, 25),
        start_time=time(22, 0),
        end_time=time(2, 0),
        dj=second_dj,
        event_title="Late Event",
        created_by=user,
    )

    assert second_booking.id is not None
    assert Booking.objects.count() == 2


@pytest.mark.django_db
def test_update_booking_should_respect_conflict_validation(user, venue, dj, second_dj):
    booking_one = create_booking(
        venue=venue,
        booking_date=date(2026, 4, 25),
        start_time=time(18, 0),
        end_time=time(21, 0),
        dj=dj,
        event_title="Early Event",
        created_by=user,
    )

    booking_two = create_booking(
        venue=venue,
        booking_date=date(2026, 4, 25),
        start_time=time(22, 0),
        end_time=time(2, 0),
        dj=second_dj,
        event_title="Late Event",
        created_by=user,
    )

    with pytest.raises(BookingConflictError):
        update_booking(
            booking=booking_two,
            start_time=time(20, 30),
            end_time=time(23, 30),
            updated_by=user,
        )

    booking_two.refresh_from_db()
    assert booking_two.start_time == time(22, 0)
    assert booking_two.end_time == time(2, 0)


@pytest.mark.django_db
def test_change_booking_status_creates_history_and_audit_log(user, venue, dj):
    booking = create_booking(
        venue=venue,
        booking_date=date(2026, 4, 25),
        start_time=time(22, 0),
        end_time=time(2, 0),
        dj=dj,
        event_title="Saturday Night Party",
        created_by=user,
    )

    updated_booking = change_booking_status(
        booking=booking,
        new_status=Booking.Status.PENDING_DJ_CONFIRMATION,
        changed_by=user,
        comment="Initial WhatsApp sent to DJ.",
    )

    assert updated_booking.status == Booking.Status.PENDING_DJ_CONFIRMATION
    assert BookingStatusHistory.objects.count() == 1

    history = BookingStatusHistory.objects.first()
    assert history.old_status == Booking.Status.TO_BOOK
    assert history.new_status == Booking.Status.PENDING_DJ_CONFIRMATION
    assert history.changed_by == user

    assert AuditLog.objects.filter(action_type=AuditLog.ActionType.STATUS_CHANGE).count() == 1


@pytest.mark.django_db
def test_create_booking_contact_log_creates_audit_log(user, venue, dj):
    booking = create_booking(
        venue=venue,
        booking_date=date(2026, 4, 25),
        start_time=time(22, 0),
        end_time=time(2, 0),
        dj=dj,
        event_title="Saturday Night Party",
        created_by=user,
    )

    contact_log = create_booking_contact_log(
        booking=booking,
        contact_type=BookingContactLog.ContactType.WHATSAPP,
        outcome=BookingContactLog.Outcome.SENT,
        contact_date=timezone.now(),
        contacted_by=user,
        notes="WhatsApp message sent to confirm booking.",
    )

    assert contact_log.id is not None
    assert contact_log.booking == booking
    assert contact_log.contacted_by == user
    assert BookingContactLog.objects.count() == 1
    assert AuditLog.objects.filter(target_model="BookingContactLog").count() == 1