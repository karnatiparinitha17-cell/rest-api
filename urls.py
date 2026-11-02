"""
URL configuration for the Appointment Booking Management System.
"""
from django.contrib import admin
from django.urls import include, path
from rest_framework.response import Response
from rest_framework.decorators import api_view


@api_view(['GET'])
def api_root_overview(request):
    """
    Project overview providing base API links and system information.
    """
    return Response({
        "project": "Appointment Booking Management System API",
        "internship": "ShadowFox Beginner-Level Backend Developer",
        "version": "1.0.0",
        "endpoints": {
            "appointments": request.build_absolute_uri('/api/appointments/'),
            "admin": request.build_absolute_uri('/admin/'),
        },
        "documentation": {
            "create": "POST /api/appointments/",
            "list": "GET /api/appointments/ (supports ?appointment_date=YYYY-MM-DD, ?status=booked|completed|cancelled, ?search=name|email)",
            "retrieve": "GET /api/appointments/<id>/",
            "update_or_reschedule": "PATCH /api/appointments/<id>/",
            "cancel": "POST /api/appointments/<id>/cancel/",
            "complete": "POST /api/appointments/<id>/complete/",
            "delete": "DELETE /api/appointments/<id>/",
        }
    })


urlpatterns = [
    path('', api_root_overview, name='api-overview'),
    path('admin/', admin.site.urls),
    path('api/', include('bookings.urls')),
]
