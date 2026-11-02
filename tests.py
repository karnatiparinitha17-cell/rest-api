import datetime
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Appointment, AppointmentStatus


class AppointmentAPITests(APITestCase):
    """
    Automated test suite verifying all REST API endpoints, business constraints,
    validation rules, and edge cases for the Appointment Booking System.
    """

    def setUp(self):
        # Dynamically set future and past dates so tests remain reliable anytime they are run
        today = timezone.localdate() if hasattr(timezone, 'localdate') else timezone.now().date()
        self.future_date_1 = today + datetime.timedelta(days=2)
        self.future_date_2 = today + datetime.timedelta(days=5)
        self.past_date = today - datetime.timedelta(days=2)

        self.time_slot_1 = datetime.time(10, 0, 0)
        self.time_slot_2 = datetime.time(14, 30, 0)

        # Base valid payload
        self.valid_payload = {
            "customer_name": "Alice Johnson",
            "email": "alice@example.com",
            "phone": "+1-555-0199",
            "service": "General Consultation",
            "appointment_date": self.future_date_1.isoformat(),
            "appointment_time": "10:00:00",
            "notes": "First time patient consultation."
        }

    # 1. Successful appointment booking
    def test_successful_appointment_booking(self):
        response = self.client.post('/api/appointments/', self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['customer_name'], "Alice Johnson")
        self.assertEqual(response.data['email'], "alice@example.com")
        self.assertEqual(response.data['status'], AppointmentStatus.BOOKED)
        self.assertIn('id', response.data)
        self.assertEqual(Appointment.objects.count(), 1)

    # 2. Missing required fields
    def test_missing_required_fields(self):
        incomplete_payload = {
            "phone": "+1-555-0199",
            "notes": "Missing required details"
        }
        response = self.client.post('/api/appointments/', incomplete_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('customer_name', response.data)
        self.assertIn('email', response.data)
        self.assertIn('service', response.data)
        self.assertIn('appointment_date', response.data)
        self.assertIn('appointment_time', response.data)

    # 3. Invalid email
    def test_invalid_email(self):
        payload = self.valid_payload.copy()
        payload['email'] = 'invalid-email-format'
        response = self.client.post('/api/appointments/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    # 4. Booking in the past
    def test_booking_in_the_past(self):
        payload = self.valid_payload.copy()
        payload['appointment_date'] = self.past_date.isoformat()
        response = self.client.post('/api/appointments/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('appointment_date', response.data)

    # 5. Listing appointments with filtering and search
    def test_listing_appointments(self):
        apt1 = Appointment.objects.create(
            customer_name="Bob Smith",
            email="bob@example.com",
            service="Dental Cleaning",
            appointment_date=self.future_date_1,
            appointment_time=self.time_slot_1,
            status=AppointmentStatus.BOOKED
        )
        apt2 = Appointment.objects.create(
            customer_name="Charlie Brown",
            email="charlie@example.com",
            service="Eye Exam",
            appointment_date=self.future_date_2,
            appointment_time=self.time_slot_2,
            status=AppointmentStatus.CANCELLED
        )

        # List all
        response = self.client.get('/api/appointments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        # Filter by status
        response_filtered = self.client.get(f'/api/appointments/?status={AppointmentStatus.CANCELLED}')
        self.assertEqual(response_filtered.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_filtered.data), 1)
        self.assertEqual(response_filtered.data[0]['customer_name'], "Charlie Brown")

        # Search by customer name
        response_search = self.client.get('/api/appointments/?search=Bob')
        self.assertEqual(response_search.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_search.data), 1)
        self.assertEqual(response_search.data[0]['customer_name'], "Bob Smith")

    # 6. Retrieving a booking
    def test_retrieving_a_booking(self):
        apt = Appointment.objects.create(
            customer_name="Diana Prince",
            email="diana@example.com",
            service="Physical Therapy",
            appointment_date=self.future_date_1,
            appointment_time=self.time_slot_1,
            status=AppointmentStatus.BOOKED
        )
        response = self.client.get(f'/api/appointments/{apt.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['customer_name'], "Diana Prince")
        self.assertEqual(response.data['service'], "Physical Therapy")

    # 7. Nonexistent appointment ID
    def test_nonexistent_appointment_id(self):
        response = self.client.get('/api/appointments/99999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # 8. Successful rescheduling
    def test_successful_rescheduling(self):
        apt = Appointment.objects.create(
            customer_name="Evan Wright",
            email="evan@example.com",
            service="Consultation",
            appointment_date=self.future_date_1,
            appointment_time=self.time_slot_1,
            status=AppointmentStatus.BOOKED
        )
        patch_payload = {
            "appointment_date": self.future_date_2.isoformat(),
            "appointment_time": "14:30:00"
        }
        response = self.client.patch(f'/api/appointments/{apt.id}/', patch_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        apt.refresh_from_db()
        self.assertEqual(apt.appointment_date, self.future_date_2)
        self.assertEqual(apt.appointment_time, datetime.time(14, 30, 0))

    # 9. Rescheduling a cancelled appointment (must be rejected)
    def test_rescheduling_a_cancelled_appointment(self):
        apt = Appointment.objects.create(
            customer_name="Fiona Gallagher",
            email="fiona@example.com",
            service="Consultation",
            appointment_date=self.future_date_1,
            appointment_time=self.time_slot_1,
            status=AppointmentStatus.CANCELLED
        )
        patch_payload = {
            "appointment_date": self.future_date_2.isoformat()
        }
        response = self.client.patch(f'/api/appointments/{apt.id}/', patch_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("cancelled", str(response.data))

    # 10. Rescheduling a completed appointment (must be rejected)
    def test_rescheduling_a_completed_appointment(self):
        apt = Appointment.objects.create(
            customer_name="George Clark",
            email="george@example.com",
            service="Consultation",
            appointment_date=self.future_date_1,
            appointment_time=self.time_slot_1,
            status=AppointmentStatus.COMPLETED
        )
        patch_payload = {
            "appointment_date": self.future_date_2.isoformat()
        }
        response = self.client.patch(f'/api/appointments/{apt.id}/', patch_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("completed", str(response.data))

    # 11. Cancelling an appointment
    def test_cancelling_an_appointment(self):
        apt = Appointment.objects.create(
            customer_name="Hannah Montana",
            email="hannah@example.com",
            service="Voice Coaching",
            appointment_date=self.future_date_1,
            appointment_time=self.time_slot_1,
            status=AppointmentStatus.BOOKED
        )
        response = self.client.post(f'/api/appointments/{apt.id}/cancel/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['appointment']['status'], AppointmentStatus.CANCELLED)
        apt.refresh_from_db()
        self.assertEqual(apt.status, AppointmentStatus.CANCELLED)

        # Repeated cancellation must be rejected
        repeat_response = self.client.post(f'/api/appointments/{apt.id}/cancel/')
        self.assertEqual(repeat_response.status_code, status.HTTP_400_BAD_REQUEST)

    # 12. Completing an appointment
    def test_completing_an_appointment(self):
        apt = Appointment.objects.create(
            customer_name="Ian Malcolm",
            email="ian@example.com",
            service="Consultation",
            appointment_date=self.future_date_1,
            appointment_time=self.time_slot_1,
            status=AppointmentStatus.BOOKED
        )
        response = self.client.post(f'/api/appointments/{apt.id}/complete/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['appointment']['status'], AppointmentStatus.COMPLETED)
        apt.refresh_from_db()
        self.assertEqual(apt.status, AppointmentStatus.COMPLETED)

        # Completed appointment cannot be cancelled
        cancel_response = self.client.post(f'/api/appointments/{apt.id}/cancel/')
        self.assertEqual(cancel_response.status_code, status.HTTP_400_BAD_REQUEST)

        # Completed appointment cannot be completed again
        repeat_complete = self.client.post(f'/api/appointments/{apt.id}/complete/')
        self.assertEqual(repeat_complete.status_code, status.HTTP_400_BAD_REQUEST)

    # 13. Duplicate time-slot prevention
    def test_duplicate_time_slot_prevention(self):
        Appointment.objects.create(
            customer_name="Existing Customer",
            email="existing@example.com",
            service="General Consultation",
            appointment_date=self.future_date_1,
            appointment_time=self.time_slot_1,
            status=AppointmentStatus.BOOKED
        )
        conflicting_payload = self.valid_payload.copy()
        conflicting_payload['customer_name'] = "New Customer"
        conflicting_payload['email'] = "new@example.com"
        conflicting_payload['appointment_date'] = self.future_date_1.isoformat()
        conflicting_payload['appointment_time'] = "10:00:00"

        response = self.client.post('/api/appointments/', conflicting_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("appointment_time", response.data)
        self.assertIn("already booked", str(response.data['appointment_time']))

    # 14. Booking a cancelled appointment's released time slot
    def test_booking_a_cancelled_appointment_released_slot(self):
        Appointment.objects.create(
            customer_name="Previous Customer",
            email="prev@example.com",
            service="Consultation",
            appointment_date=self.future_date_1,
            appointment_time=self.time_slot_1,
            status=AppointmentStatus.CANCELLED
        )
        # Attempting to book the same slot must succeed because the previous booking was cancelled
        response = self.client.post('/api/appointments/', self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], AppointmentStatus.BOOKED)

    # 15. Successful deletion
    def test_successful_deletion(self):
        apt = Appointment.objects.create(
            customer_name="Jack Sparrow",
            email="jack@example.com",
            service="Consultation",
            appointment_date=self.future_date_1,
            appointment_time=self.time_slot_1,
            status=AppointmentStatus.BOOKED
        )
        response = self.client.delete(f'/api/appointments/{apt.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Appointment.objects.filter(id=apt.id).exists())

    # 16. Method not allowed for unsupported HTTP methods (e.g., PUT)
    def test_method_not_allowed_on_put(self):
        apt = Appointment.objects.create(
            customer_name="Kevin Flynn",
            email="kevin@example.com",
            service="Consultation",
            appointment_date=self.future_date_1,
            appointment_time=self.time_slot_1,
            status=AppointmentStatus.BOOKED
        )
        response = self.client.put(f'/api/appointments/{apt.id}/', self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # 17. Malformed JSON handling
    def test_malformed_json_request(self):
        response = self.client.post(
            '/api/appointments/',
            data='{"invalid_json": ',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # 18. Database-level unique constraint enforces conflict even if bypassed
    def test_database_unique_constraint(self):
        from django.db import IntegrityError
        Appointment.objects.create(
            customer_name="Direct DB 1",
            email="db1@example.com",
            service="Checkup",
            appointment_date=self.future_date_1,
            appointment_time=self.time_slot_1,
            status=AppointmentStatus.BOOKED
        )
        with self.assertRaises(IntegrityError):
            Appointment.objects.create(
                customer_name="Direct DB 2",
                email="db2@example.com",
                service="Checkup",
                appointment_date=self.future_date_1,
                appointment_time=self.time_slot_1,
                status=AppointmentStatus.BOOKED
            )

