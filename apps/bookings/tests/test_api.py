import pytest
from datetime import date

from apps.audit.models import AuditLog
from apps.bookings.models import Booking
from apps.booking_contact_log.models import BookingContactLog
from apps.djs.models import DJ, Genre


@pytest.mark.django_db
def test_protected_endpoint_requires_authentication(api_client, venue):
    response = api_client.get("/api/venues/")
    assert response.status_code in [401, 403]


@pytest.mark.django_db
def test_login_endpoint_returns_authenticated_user(api_client, user):
    response = api_client.post(
        "/api/auth/login/",
        {
            "email": user.email,
            "password": "StrongPassword123",
        },
        format="json",
    )

    assert response.status_code == 200
    assert response.data["detail"] == "Login successful."
    assert response.data["user"]["email"] == user.email


@pytest.mark.django_db
def test_me_endpoint_returns_current_user(authenticated_client, user):
    response = authenticated_client.get("/api/auth/me/")

    assert response.status_code == 200
    assert response.data["email"] == user.email
    assert response.data["role"] == "admin"


@pytest.mark.django_db
def test_create_genre_via_api(authenticated_client):
    response = authenticated_client.post(
        "/api/genres/",
        {
            "name": "House",
            "slug": "house",
            "description": "House music genre",
        },
        format="json",
    )

    assert response.status_code == 201
    assert Genre.objects.count() == 1
    assert response.data["name"] == "House"


@pytest.mark.django_db
def test_create_dj_via_api(authenticated_client, genre):
    response = authenticated_client.post(
        "/api/djs/",
        {
            "full_name": "Sarah Example",
            "stage_name": "DJ Sarah",
            "phone": "+33611111111",
            "email": "djsarah@test.com",
            "genres": [genre.id],
            "notes": "Good for Friday nights",
            "is_active": True,
        },
        format="json",
    )

    assert response.status_code == 201
    assert DJ.objects.count() == 1
    assert response.data["stage_name"] == "DJ Sarah"


@pytest.mark.django_db
def test_create_booking_via_api(authenticated_client, venue, dj):
    response = authenticated_client.post(
        "/api/bookings/",
        {
            "venue": venue.id,
            "booking_date": "2026-04-25",
            "start_time": "22:00:00",
            "end_time": "02:00:00",
            "dj": dj.id,
            "event_title": "Saturday Night Party",
            "status": "to_book",
            "notes": "Initial booking for weekend set",
            "unusual_hours": False,
        },
        format="json",
    )

    assert response.status_code == 201
    assert Booking.objects.count() == 1
    assert response.data["event_title"] == "Saturday Night Party"
    assert response.data["status"] == "to_book"


@pytest.mark.django_db
def test_change_booking_status_via_api(authenticated_client, venue, dj):
    create_response = authenticated_client.post(
        "/api/bookings/",
        {
            "venue": venue.id,
            "booking_date": "2026-04-25",
            "start_time": "22:00:00",
            "end_time": "02:00:00",
            "dj": dj.id,
            "event_title": "Saturday Night Party",
            "status": "to_book",
            "notes": "Initial booking for weekend set",
            "unusual_hours": False,
        },
        format="json",
    )
    booking_id = create_response.data["id"]

    response = authenticated_client.post(
        f"/api/bookings/{booking_id}/change-status/",
        {
            "new_status": "pending_dj_confirmation",
            "comment": "WhatsApp sent to DJ",
        },
        format="json",
    )

    assert response.status_code == 200
    assert response.data["status"] == "pending_dj_confirmation"


@pytest.mark.django_db
def test_create_contact_log_via_api(authenticated_client, venue, dj):
    create_response = authenticated_client.post(
        "/api/bookings/",
        {
            "venue": venue.id,
            "booking_date": "2026-04-25",
            "start_time": "22:00:00",
            "end_time": "02:00:00",
            "dj": dj.id,
            "event_title": "Saturday Night Party",
            "status": "to_book",
            "notes": "Initial booking for weekend set",
            "unusual_hours": False,
        },
        format="json",
    )
    booking_id = create_response.data["id"]

    response = authenticated_client.post(
        f"/api/bookings/{booking_id}/contact-logs/",
        {
            "contact_type": "whatsapp",
            "contact_date": "2026-04-21",
            "outcome": "sent",
            "notes": "Initial WhatsApp message sent to confirm booking",
        },
        format="json",
    )

    assert response.status_code == 201
    assert BookingContactLog.objects.count() == 1
    assert response.data["contact_type"] == "whatsapp"
    assert response.data["outcome"] == "sent"


@pytest.mark.django_db
def test_audit_logs_are_admin_accessible(authenticated_client, venue, dj):
    authenticated_client.post(
        "/api/bookings/",
        {
            "venue": venue.id,
            "booking_date": "2026-04-25",
            "start_time": "22:00:00",
            "end_time": "02:00:00",
            "dj": dj.id,
            "event_title": "Saturday Night Party",
            "status": "to_book",
            "notes": "Initial booking for weekend set",
            "unusual_hours": False,
        },
        format="json",
    )

    response = authenticated_client.get("/api/audit-logs/")

    assert response.status_code == 200
    assert AuditLog.objects.count() >= 1
    assert isinstance(response.data, list) or "results" in response.data