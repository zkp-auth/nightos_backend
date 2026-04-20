from django.db import models
from apps.common.models import TimeStampedModel

# Create your models here.
class Venue(TimeStampedModel):
    """
    Represents a venues managed by the platform.

    The project starts with O'Sullivans venues, but the model is kept
    generic so the platform can support other nightlife  brands in the future.
    """
    name =  models.CharField(
        max_length=150,
        unique=True,
        help_text="Public venues name shown in the platform.",
    )
    slug = models.SlugField(
        max_length=150,
        unique=True,
        help_text="Stable unique identifier used in URLs and filtering.",
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        help_text="City where the venues is located.",
    )
    address = models.CharField(
        max_length=255,
        help_text="Venue address, optional for the MVP.",
    )
    timezone = models.CharField(
        max_length=64,
        blank=True,
        help_text="Timezone of the venues, used for scheduling and date/time logic.",
    )

    class Meta:
        db_table = "venues"
        ordering = ["name"]

    def __str__(self):
        return self.name







