from django.contrib import admin
from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'customer_name',
        'email',
        'phone',
        'service',
        'appointment_date',
        'appointment_time',
        'status',
        'created_at',
    )
    list_filter = ('status', 'appointment_date', 'service')
    search_fields = ('customer_name', 'email', 'phone', 'service')
    date_hierarchy = 'appointment_date'
    ordering = ('appointment_date', 'appointment_time')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Customer Information', {
            'fields': ('customer_name', 'email', 'phone')
        }),
        ('Appointment Details', {
            'fields': ('service', 'appointment_date', 'appointment_time', 'notes', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
