from urllib import response

import pytest
from rest_framework.test import APIClient

from apps.accounts.models import CustomUser
from apps.djs.models import DJ, Genre
from apps.venues.models import Venue


@pytest.fixture
def user(db):
    return CustomUser.objects.create_user(
        email="admin@test.com",
        password="StrongPassword123",
        first_name="Admin",
        last_name="User",
        role="admin",
        is_staff=True,
    )


@pytest.fixture
def venue(db):
    return Venue.objects.create(
        name="O'Sullivans Grands Boulevards",
        slug="osullivans-grands-boulevards",
        city="Paris",
        timezone="Europe/Paris",
        is_active=True,
    )


@pytest.fixture
def second_venue(db):
    return Venue.objects.create(
        name="O'Sullivans Rebel Bar",
        slug="osullivans-rebel-bar",
        city="Paris",
        timezone="Europe/Paris",
        is_active=True,
    )


@pytest.fixture
def genre(db):
    return Genre.objects.create(
        name="Afrobeat",
        slug="afrobeat",
        description="Popular Afro club genre",
    )


@pytest.fixture
def dj(db, genre):
    dj = DJ.objects.create(
        full_name="Mike Air",
        stage_name="DJ Mike",
        phone="+33600000000",
        email="djmike@test.com",
        is_active=True,
    )
    dj.genres.add(genre)
    return dj


@pytest.fixture
def second_dj(db):
    return DJ.objects.create(
        full_name="Sarah Example",
        stage_name="DJ Sarah",
        phone="+33611111111",
        email="djsarah@test.com",
        is_active=True,
    )

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def authenticated_client(user):
    client = APIClient()
    response = client.post(
        "/api/auth/login/",
        {
            "email":user.email,
            "password":"StrongPassword123",
        }
    )
    assert response.status_code == 200
    # login_successful = client.login(email=user.email, password="StrongPassword123")
    # assert login_successful is True
    return client