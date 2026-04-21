from rest_framework import viewsets
from apps.accounts.permissions import IsAdminOrManager
from .models import DJ, Genre
from .serializers import DJSerializer, DJWriteSerializer, GenreSerializer

class GenreViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing music genres.
    """

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAdminOrManager]
    filterset_fields = ["name", "slug"]
    search_fields = ["name", "slug"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]

class DJViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing DJs.
    Use separate serializers for read and write operations.
    """

    queryset = DJ.objects.prefetch_related("genres").all()
    permission_classes = [IsAdminOrManager]
    filterset_fields = ["is_active", "genres"]
    search_fields = ["full_name", "stage_name", "phone", "email"]
    ordering_fields = ["stage_name", "full_name", "created_at"]
    ordering = ["stage_name", "full_name"]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return DJWriteSerializer
        return DJSerializer

