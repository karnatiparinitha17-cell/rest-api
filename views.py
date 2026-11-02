from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Appointment, AppointmentStatus
from .serializers import AppointmentSerializer


class AppointmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Appointments.
    Supports:
    - POST /api/appointments/ -> Create booking (201 Created)
    - GET /api/appointments/ -> List all bookings with filtering & search (200 OK)
    - GET /api/appointments/<id>/ -> Retrieve single booking (200 OK / 404 Not Found)
    - PATCH /api/appointments/<id>/ -> Update / reschedule booking (200 OK / 400 Bad Request)
    - DELETE /api/appointments/<id>/ -> Delete booking (204 No Content)
    - POST /api/appointments/<id>/cancel/ -> Cancel appointment (200 OK / 400 Bad Request)
    - POST /api/appointments/<id>/complete/ -> Complete appointment (200 OK / 400 Bad Request)
    """
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    # Filtering, Searching, and Ordering
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['appointment_date', 'status']
    search_fields = ['customer_name', 'email']
    ordering_fields = ['appointment_date', 'appointment_time', 'created_at']
    ordering = ['appointment_date', 'appointment_time']

    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request, pk=None):
        """
        Cancels an active appointment.
        Prevents repeated cancellation or cancellation of completed appointments.
        """
        appointment = self.get_object()

        if appointment.status == AppointmentStatus.CANCELLED:
            return Response(
                {"error": "This appointment has already been cancelled."},
                status=status.HTTP_400_BAD_REQUEST
            )
        if appointment.status == AppointmentStatus.COMPLETED:
            return Response(
                {"error": "A completed appointment cannot be cancelled."},
                status=status.HTTP_400_BAD_REQUEST
            )

        appointment.status = AppointmentStatus.CANCELLED
        appointment.save(update_fields=['status', 'updated_at'])
        serializer = self.get_serializer(appointment)
        return Response(
            {
                "message": "Appointment cancelled successfully.",
                "appointment": serializer.data
            },
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'], url_path='complete')
    def complete(self, request, pk=None):
        """
        Marks an appointment as completed.
        Validates that cancelled appointments cannot be marked completed
        and prevents duplicate completion.
        """
        appointment = self.get_object()

        if appointment.status == AppointmentStatus.CANCELLED:
            return Response(
                {"error": "A cancelled appointment cannot be marked as completed."},
                status=status.HTTP_400_BAD_REQUEST
            )
        if appointment.status == AppointmentStatus.COMPLETED:
            return Response(
                {"error": "This appointment has already been marked as completed."},
                status=status.HTTP_400_BAD_REQUEST
            )

        appointment.status = AppointmentStatus.COMPLETED
        appointment.save(update_fields=['status', 'updated_at'])
        serializer = self.get_serializer(appointment)
        return Response(
            {
                "message": "Appointment marked as completed successfully.",
                "appointment": serializer.data
            },
            status=status.HTTP_200_OK
        )
