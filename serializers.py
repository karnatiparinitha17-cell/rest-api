import datetime
from django.utils import timezone
from rest_framework import serializers
from .models import Appointment, AppointmentStatus


class AppointmentSerializer(serializers.ModelSerializer):
    """
    Serializer for Appointment model supporting validation of customer details,
    future schedule constraints, slot conflict checking, and status lifecycle guards.
    """

    class Meta:
        model = Appointment
        fields = [
            'id',
            'customer_name',
            'email',
            'phone',
            'service',
            'appointment_date',
            'appointment_time',
            'notes',
            'status',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'status', 'created_at', 'updated_at']
        validators = []

    def validate_customer_name(self, value):
        stripped = value.strip()
        if not stripped:
            raise serializers.ValidationError("Customer name cannot be blank or contain only whitespace.")
        return stripped

    def validate_service(self, value):
        stripped = value.strip()
        if not stripped:
            raise serializers.ValidationError("Service cannot be blank or contain only whitespace.")
        return stripped

    def validate(self, attrs):
        instance = getattr(self, 'instance', None)

        # 1. Lifecycle check for updates/reschedules
        if instance is not None:
            if instance.status == AppointmentStatus.CANCELLED:
                raise serializers.ValidationError(
                    {"error": "A cancelled appointment cannot be modified or rescheduled."}
                )
            if instance.status == AppointmentStatus.COMPLETED:
                raise serializers.ValidationError(
                    {"error": "A completed appointment cannot be modified or rescheduled."}
                )

        # 2. Extract target date and time (from payload or instance fallback)
        target_date = attrs.get('appointment_date', instance.appointment_date if instance else None)
        target_time = attrs.get('appointment_time', instance.appointment_time if instance else None)

        if target_date is not None and target_time is not None:
            # 3. Check for past date/time
            now = timezone.localtime() if timezone.is_aware(timezone.now()) else timezone.now()
            combined_dt = datetime.datetime.combine(target_date, target_time)
            if timezone.is_aware(now):
                combined_dt = timezone.make_aware(combined_dt, timezone.get_current_timezone())

            if combined_dt < now:
                raise serializers.ValidationError({
                    "appointment_date": "Appointments cannot be scheduled in the past. Please select a future date and time."
                })

            # 4. Check for slot conflict among active appointments
            # Cancelled appointments do NOT block slots.
            conflict_qs = Appointment.objects.filter(
                appointment_date=target_date,
                appointment_time=target_time,
                status__in=[AppointmentStatus.BOOKED, AppointmentStatus.COMPLETED]
            )
            if instance is not None:
                conflict_qs = conflict_qs.exclude(pk=instance.pk)

            if conflict_qs.exists():
                formatted_time = target_time.strftime('%H:%M') if hasattr(target_time, 'strftime') else str(target_time)
                raise serializers.ValidationError({
                    "appointment_time": f"The slot on {target_date} at {formatted_time} is already booked. Please choose another time slot."
                })

        return attrs
