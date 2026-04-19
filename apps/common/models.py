from django.db import models


class TimeStampedModel(models.Model):
    """
    Abstract base model that provides reusable timestamp fields.

    This avoids duplication across models and ensures consistency.
    """

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Date and time when the record was created"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Date and time when the record was last updated"
    )

    class Meta:
        abstract = True