from rest_framework import viewsets
from apps.accounts.permissions import IsAdminOrManager
from .models import Venue
from .serializers import VenueSerializer



class VenueViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing venues.
    """

    queryset = Venue.objects.all()
    serializer_class = VenueSerializer
    permission_classes = [IsAdminOrManager]
    filterset_fields = ["is_active", "city"]
    search_fields = ["name", "slug", "city"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]

