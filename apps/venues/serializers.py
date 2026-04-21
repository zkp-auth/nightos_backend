from rest_framework import serializers
from .models import Venue

class VenueSerializer(serializers.ModelSerializer):
    """Serializer for the venue read/write operations."""

    class Meta:
        model = Venue
        fields = [
            "id",
            "name",
            "slug",
            "city",
            "address",
            "timezone",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]