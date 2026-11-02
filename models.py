from django.db import models
from django.utils import timezone
import datetime


class AppointmentStatus(models.TextChoices):
    BOOKED = 'booked', 'Booked'
    COMPLETED = 'completed', 'Completed'
    CANCELLED = 'cancelled', 'Cancelled'


class Appointment(models.Model):
    """
    Appointment model storing customer booking information,
    service details, schedule, status, and audit timestamps.
    """
    customer_name = models.CharField(
        max_length=150,
        help_text="Full name of the customer booking the appointment."
    )
    email = models.EmailField(
        max_length=254,
        help_text="Valid email address for appointment confirmation and notifications."
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        default="",
        help_text="Optional contact telephone number."
    )
    service = models.CharField(
        max_length=150,
        help_text="Service type or purpose of the appointment."
    )
    appointment_date = models.DateField(
        help_text="Scheduled date for the appointment (YYYY-MM-DD)."
    )
    appointment_time = models.TimeField(
        help_text="Scheduled time for the appointment (HH:MM:SS or HH:MM)."
    )
    notes = models.TextField(
        blank=True,
        default="",
        help_text="Optional notes or instructions for the appointment."
    )
    status = models.CharField(
        max_length=20,
        choices=AppointmentStatus.choices,
        default=AppointmentStatus.BOOKED,
        help_text="Current lifecycle state of the appointment."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the appointment was originally created."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the appointment record was last modified."
    )

    class Meta:
        ordering = ['appointment_date', 'appointment_time']
        verbose_name = 'Appointment'
        verbose_name_plural = 'Appointments'
        constraints = [
            models.UniqueConstraint(
                fields=['appointment_date', 'appointment_time'],
                condition=models.Q(status__in=[AppointmentStatus.BOOKED, AppointmentStatus.COMPLETED]),
                name='unique_active_appointment_date_time'
            )
        ]

    def __str__(self):
        return f"{self.customer_name} - {self.service} on {self.appointment_date} at {self.appointment_time} ({self.status})"

    @property
    def appointment_datetime(self):
        """Combines appointment_date and appointment_time into a timezone-aware or naive datetime object."""
        combined = datetime.datetime.combine(self.appointment_date, self.appointment_time)
        if timezone.is_aware(timezone.now()):
            return timezone.make_aware(combined, timezone.get_current_timezone())
        return combined

    def is_in_past(self):
        """Checks if the appointment scheduled datetime is in the past."""
        return self.appointment_datetime < timezone.now()
