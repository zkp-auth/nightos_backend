from django.db import models
from apps.common.models import TimeStampedModel


class Genre(TimeStampedModel):
    """
    Represents a music genre that can be associated with one or more DJs.

    A separate model keeps genre data normalized and avoids inconsistencies
    caused by free-text values such as spelling variations.
    """

    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Display name of the genre (e.g., Afrobeat, House Music, Techno, Hip-Hop, Shatta,  Bouyon).",
    )
    slug = models.SlugField(
        unique=True,
        help_text="Stable unique identifier used in filtering and URLs.",
    )
    description = models.TextField(
        blank=True,
        help_text="Optional internal description of the genre (eg. generalist).",
    )
    class Meta:
        db_table = "genres"
        ordering = ["name"]

    def __str__(self):
        return self.name

class DJ(TimeStampedModel):
    """
    Represents a DJ that can be booked for events.

    The model is intentionally simple for the MVP, while keeping room
    for future features such as reliability scoring, availability,
    and AI-based recommendations.
    """

    full_name = models.CharField(
        max_length=150,
        help_text="Legal or full name of the DJ.",
    )
    stage_name = models.CharField(
        max_length=150,
        unique=True,
        blank=True,
        null=True,
        help_text="Public/stage name used for events.",
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        help_text="Primary contact number, often used for Whatsapp communication.",
    )
    email = models.EmailField(
        blank=True,
        help_text="Optional email address.",
    )
    genres = models.ManyToManyField(
        Genre,
        blank=True,
        related_name="djs",
        help_text="Musical genres associated with the DJ.",
    )
    notes = models.TextField(
        blank=True,
        help_text="Internal notes about preferences or operational comments.",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Deactivate the DJ without deleting historical bookings.",
    )

    class Meta:
        db_table = "djs"
        ordering = ["stage_name", "full_name"]

    def __str__(self):
        return self.stage_name or self.full_name


