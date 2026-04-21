from django.core.serializers import serialize
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.accounts.permissions import IsAdminOrManager
from .models import Booking
from apps.booking_contact_log.models import BookingContactLog
from apps.booking_status_history.models import BookingStatusHistory
from .serializers import (
    BookingContactLogSerializer,
    BookingSerializer,
    BookingStatusHistorySerializer,
    ChangeBookingStatusSerializer,
    CreateBookingSerializer,
    UpdateBookingSerializer
)


class BookingViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing bookings.

    Read and write operations are separated to keep the API clean and
    allows the service layer to control the business logic.
    """

    queryset = (
        Booking.objects.select_related("venue", "dj", "created_by", "updated_by")
        .prefetch_related("status_history", "contact_logs")
        .all()
    )
    permission_classes = [IsAdminOrManager]
    filterset_fields = ["venue", "status", "unusual_hours", "booking_date", "dj"]
    search_fields = ["event_title", "notes", "venue__name", "dj__stage_name"]
    ordering_fields = ["booking_date", "start_time", "created_at"]
    ordering = ["booking_date", "start_time"]

    def get_serializer_class(self):
        if self.action == "create":
            return CreateBookingSerializer
        if self.action in ["update", "partial_update"]:
            return UpdateBookingSerializer
        return BookingSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        booking = serializer.save()

        response_serializer = BookingSerializer(booking, context={"request": request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        booking = self.get_object()
        serializer = self.get_serializer(
            instance=booking,
            data=request.data,
            partial=False,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        updated_booking = serializer.save()

        response_serializer = BookingSerializer(updated_booking, context={"request": request})
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        booking = self.get_object()
        serializer = self.get_serializer(
            instance=booking,
            data=request.data,
            partial=True,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        updated_booking = serializer.save()

        response_serializer = BookingSerializer(updated_booking, context={"request": request})
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="change-status")
    def change_status(self, request, pk=None):
        """
        Custom endpoint to change the booking status while automatically
        recording status history and audit logs.
        """
        booking = self.get_object()
        serializer = ChangeBookingStatusSerializer(
            data=request.data,
            context={"request": request, "booking": booking},
        )
        serializer.is_valid(raise_exception=True)
        updated_booking = serializer.save()

        response_serializer = BookingSerializer(updated_booking, context={"request": request})
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_path="status-history")
    def status_history(self, request, pk=None):
        """
        Return status history entries for a booking.
        """
        booking = self.get_object()
        history = booking.status_history.select_related("changed_by").all()
        serializer = BookingStatusHistorySerializer(history, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get", "post"], url_path="contact-logs")
    def contact_logs(self, request, pk=None):
        """
        GET: list booking contact logs
        POST: create a new contact log entry for the booking
        """
        booking = self.get_object()

        if request.method == "GET":
            logs = booking.contact_logs.select_related("contacted_by").all()
            serializer = BookingContactLogSerializer(logs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        serializer = CreateBookingSerializer(
            data=request.data,
            context={"request": request, "booking": booking},
        )
        serializer.is_valid(raise_exception=True)
        contact_log = serializer.save()

        response_serializer = BookingContactLogSerializer(contact_log)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)





