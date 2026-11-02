import os
import django
import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.utils import timezone
from bookings.models import Appointment, AppointmentStatus

def seed():
    # Clear existing demo data
    Appointment.objects.all().delete()
    print("Cleared existing appointments.")

    today = timezone.localdate() if hasattr(timezone, 'localdate') else timezone.now().date()

    appointments = [
        {
            "customer_name": "Aarav Sharma",
            "email": "aarav.sharma@example.com",
            "phone": "+91-9876543210",
            "service": "General Physician Consultation",
            "appointment_date": today + datetime.timedelta(days=1),
            "appointment_time": datetime.time(10, 0, 0),
            "notes": "Routine annual checkup",
            "status": AppointmentStatus.BOOKED
        },
        {
            "customer_name": "Priya Patel",
            "email": "priya.patel@example.com",
            "phone": "+91-9876543211",
            "service": "Dental Scaling & Polishing",
            "appointment_date": today + datetime.timedelta(days=2),
            "appointment_time": datetime.time(11, 30, 0),
            "notes": "Sensitive gums",
            "status": AppointmentStatus.BOOKED
        },
        {
            "customer_name": "Rohan Gupta",
            "email": "rohan.gupta@example.com",
            "phone": "+91-9876543212",
            "service": "Eye Vision Test",
            "appointment_date": today + datetime.timedelta(days=3),
            "appointment_time": datetime.time(14, 0, 0),
            "notes": "Computer vision syndrome check",
            "status": AppointmentStatus.BOOKED
        },
        {
            "customer_name": "Sneha Reddy",
            "email": "sneha.reddy@example.com",
            "phone": "+91-9876543213",
            "service": "Dermatology Skin Consultation",
            "appointment_date": today - datetime.timedelta(days=3),
            "appointment_time": datetime.time(16, 0, 0),
            "notes": "Follow-up visit",
            "status": AppointmentStatus.COMPLETED
        },
        {
            "customer_name": "Vikram Singh",
            "email": "vikram.singh@example.com",
            "phone": "+91-9876543214",
            "service": "Cardiology Consultation",
            "appointment_date": today + datetime.timedelta(days=4),
            "appointment_time": datetime.time(9, 30, 0),
            "notes": "Cancelled by patient due to travel",
            "status": AppointmentStatus.CANCELLED
        }
    ]

    for item in appointments:
        apt = Appointment.objects.create(**item)
        print(f"Created: ID {apt.id} - {apt.customer_name} ({apt.service}) [{apt.status}]")

    print("\nDatabase seeded successfully!")

if __name__ == '__main__':
    seed()
