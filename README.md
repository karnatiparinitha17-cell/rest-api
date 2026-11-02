# Appointment Booking Management System

> **ShadowFox Beginner-Level Backend Developer Internship Project**  
> Developed with **Python**, **Django**, and **Django REST Framework (DRF)**.

---

## 1. Project Overview

The **Appointment Booking Management System** is a robust, production-ready RESTful backend API designed to handle the complete lifecycle of customer appointment reservations. The system allows clients to book appointments, view existing bookings, filter and search records, reschedule appointments, cancel them, mark them as completed, and delete records.

Key architectural and business features:
- **Strict Schedule Validation**: Prevents scheduling appointments in the past (both date and time).
- **Concurrency & Conflict Prevention**: Active appointments (`booked` or `completed`) cannot share the same date and time slot.
- **Dynamic Slot Release**: Once an appointment is `cancelled`, its reserved time slot is immediately released and made available for other clients.
- **Immutable State Guards**: Cancelled appointments cannot be rescheduled; completed appointments cannot be cancelled or rescheduled.
- **Comprehensive Test Suite**: 18 automated test cases covering valid flows, invalid payloads, edge cases, and database constraints.
- **Ready-to-use Postman Collection**: Importable collection for rapid API exploration and verification.

---

## 2. Technology Stack

- **Language**: Python 3.10+ (tested on Python 3.14)
- **Framework**: Django 5.x / 6.x
- **API Toolkit**: Django REST Framework (DRF) 3.15+
- **Filtering Engine**: django-filter 24.x+
- **Database**: SQLite3 (with partial unique constraints)
- **API Testing**: DRF `APITestCase` & Postman Collection v2.1
- **IDE Compatibility**: VS Code / Antigravity with virtual environment support

---

## 3. Project Directory Structure

```text
appointment_booking/
│
├── .venv/                      # Python virtual environment
├── config/                     # Core Django project configuration
│   ├── __init__.py
│   ├── asgi.py                 # ASGI entry point
│   ├── settings.py             # Django & DRF configuration
│   ├── urls.py                 # Top-level URL routing
│   └── wsgi.py                 # WSGI entry point
│
├── bookings/                   # Bookings application module
│   ├── migrations/             # Database migration files
│   │   ├── 0001_initial.py
│   │   └── __init__.py
│   ├── __init__.py
│   ├── admin.py                # Django Admin panel registration
│   ├── apps.py                 # Application configuration
│   ├── models.py               # Appointment model and constraints
│   ├── serializers.py          # Data validation & serialization
│   ├── tests.py                # 18 automated test cases
│   ├── urls.py                 # App-level API routing
│   └── views.py                # API ViewSet and action methods
│
├── db.sqlite3                  # SQLite database
├── manage.py                   # Django management script
├── postman_collection.json     # Importable Postman v2.1 collection
├── requirements.txt            # Project dependencies
├── seed_data.py                # Database seed script for quick demo
└── README.md                   # Comprehensive documentation
```

---

## 4. Setup and Installation Guide

### Prerequisites
- Python 3.10 or higher installed.
- Git (optional).

### Step 1: Open Terminal in Project Directory
```powershell
cd C:\Users\kelam\.gemini\antigravity\scratch\appointment_booking
```

### Step 2: Create and Activate Virtual Environment
**Windows PowerShell:**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

*(On macOS / Linux):*
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Required Dependencies
```powershell
pip install -r requirements.txt
```

### Step 4: Apply Database Migrations
```powershell
python manage.py makemigrations bookings
python manage.py migrate
```

### Step 5: (Optional) Seed Sample Appointments
To populate the database with realistic demo appointments:
```powershell
python seed_data.py
```

### Step 6: Create Admin Superuser (Optional)
```powershell
python manage.py createsuperuser
```

### Step 7: Run Development Server
```powershell
python manage.py runserver 127.0.0.1:8000
```
The server will start at `http://127.0.0.1:8000/`.

---

## 5. Database Schema: `Appointment`

| Field Name | Type | Options / Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | BigAutoField | Primary Key, Auto-increment | Unique identifier for the appointment |
| `customer_name`| CharField(150) | `null=False`, `blank=False` | Full name of the customer |
| `email` | EmailField(254) | `null=False`, `blank=False` | Valid customer contact email |
| `phone` | CharField(20) | `blank=True`, `default=""` | Optional contact telephone number |
| `service` | CharField(150) | `null=False`, `blank=False` | Service or medical purpose |
| `appointment_date` | DateField | `null=False` | Scheduled date (`YYYY-MM-DD`) |
| `appointment_time` | TimeField | `null=False` | Scheduled time (`HH:MM:SS`) |
| `notes` | TextField | `blank=True`, `default=""` | Optional notes or instructions |
| `status` | CharField(20) | Choices: `booked`, `completed`, `cancelled` (Default: `booked`) | Current lifecycle status |
| `created_at` | DateTimeField | `auto_now_add=True` | Record creation timestamp |
| `updated_at` | DateTimeField | `auto_now=True` | Record last modification timestamp |

### Database Constraints
- **Partial Unique Constraint**: `unique_active_appointment_date_time`
  ```python
  models.UniqueConstraint(
      fields=['appointment_date', 'appointment_time'],
      condition=models.Q(status__in=['booked', 'completed']),
      name='unique_active_appointment_date_time'
  )
  ```
  *Enforces that no two active appointments can have the exact same date and time slot, while allowing cancelled appointments to release the slot.*

---

## 6. REST API Endpoints Specification

Base URL: `http://127.0.0.1:8000/api/`

| Method | Endpoint | Description | Status Code |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | API Root Overview & endpoint index | `200 OK` |
| `POST` | `/api/appointments/` | Book a new appointment | `201 Created` / `400 Bad Request` |
| `GET` | `/api/appointments/` | List all appointments (supports filter/search) | `200 OK` |
| `GET` | `/api/appointments/<id>/` | Retrieve details of a specific appointment | `200 OK` / `404 Not Found` |
| `PATCH` | `/api/appointments/<id>/` | Reschedule or update appointment details | `200 OK` / `400 Bad Request` |
| `POST` | `/api/appointments/<id>/cancel/` | Cancel an appointment | `200 OK` / `400 Bad Request` |
| `POST` | `/api/appointments/<id>/complete/` | Mark an appointment as completed | `200 OK` / `400 Bad Request` |
| `DELETE` | `/api/appointments/<id>/` | Delete an appointment record | `204 No Content` / `404 Not Found` |

---

## 7. Endpoint Examples & Payloads

### A. Create Appointment
- **Endpoint**: `POST /api/appointments/`
- **Headers**: `Content-Type: application/json`
- **Request Body**:
```json
{
  "customer_name": "Kavya Menon",
  "email": "kavya.menon@example.com",
  "phone": "+91-9876543220",
  "service": "Physiotherapy Assessment",
  "appointment_date": "2026-10-25",
  "appointment_time": "15:00:00",
  "notes": "First rehabilitation session for shoulder."
}
```
- **Response (`201 Created`)**:
```json
{
  "id": 6,
  "customer_name": "Kavya Menon",
  "email": "kavya.menon@example.com",
  "phone": "+91-9876543220",
  "service": "Physiotherapy Assessment",
  "appointment_date": "2026-10-25",
  "appointment_time": "15:00:00",
  "notes": "First rehabilitation session for shoulder.",
  "status": "booked",
  "created_at": "2026-10-18T17:36:59.123456Z",
  "updated_at": "2026-10-18T17:36:59.123456Z"
}
```

### B. List Appointments (with Filtering & Search)
- **Endpoint**: `GET /api/appointments/`
- **Supported Query Parameters**:
  - `?status=booked` or `?status=completed` or `?status=cancelled`
  - `?appointment_date=2026-10-25`
  - `?search=Kavya` (matches against `customer_name` or `email`)
  - `?ordering=appointment_date,appointment_time`
- **Response (`200 OK`)**:
```json
[
  {
    "id": 6,
    "customer_name": "Kavya Menon",
    "email": "kavya.menon@example.com",
    "phone": "+91-9876543220",
    "service": "Physiotherapy Assessment",
    "appointment_date": "2026-10-25",
    "appointment_time": "15:00:00",
    "notes": "First rehabilitation session for shoulder.",
    "status": "booked",
    "created_at": "2026-10-18T17:36:59.123456Z",
    "updated_at": "2026-10-18T17:36:59.123456Z"
  }
]
```

### C. Retrieve Appointment
- **Endpoint**: `GET /api/appointments/6/`
- **Response (`200 OK`)**:
```json
{
  "id": 6,
  "customer_name": "Kavya Menon",
  "email": "kavya.menon@example.com",
  "phone": "+91-9876543220",
  "service": "Physiotherapy Assessment",
  "appointment_date": "2026-10-25",
  "appointment_time": "15:00:00",
  "notes": "First rehabilitation session for shoulder.",
  "status": "booked",
  "created_at": "2026-10-18T17:36:59.123456Z",
  "updated_at": "2026-10-18T17:36:59.123456Z"
}
```

### D. Reschedule Appointment
- **Endpoint**: `PATCH /api/appointments/6/`
- **Request Body**:
```json
{
  "appointment_date": "2026-10-26",
  "appointment_time": "16:30:00",
  "notes": "Rescheduled as requested by patient."
}
```
- **Response (`200 OK`)**:
```json
{
  "id": 6,
  "customer_name": "Kavya Menon",
  "email": "kavya.menon@example.com",
  "phone": "+91-9876543220",
  "service": "Physiotherapy Assessment",
  "appointment_date": "2026-10-26",
  "appointment_time": "16:30:00",
  "notes": "Rescheduled as requested by patient.",
  "status": "booked",
  "created_at": "2026-10-18T17:36:59.123456Z",
  "updated_at": "2026-10-18T17:37:02.654321Z"
}
```

### E. Cancel Appointment
- **Endpoint**: `POST /api/appointments/6/cancel/`
- **Response (`200 OK`)**:
```json
{
  "message": "Appointment cancelled successfully.",
  "appointment": {
    "id": 6,
    "customer_name": "Kavya Menon",
    "email": "kavya.menon@example.com",
    "phone": "+91-9876543220",
    "service": "Physiotherapy Assessment",
    "appointment_date": "2026-10-26",
    "appointment_time": "16:30:00",
    "notes": "Rescheduled as requested by patient.",
    "status": "cancelled",
    "created_at": "2026-10-18T17:36:59.123456Z",
    "updated_at": "2026-10-18T17:37:04.987654Z"
  }
}
```

### F. Complete Appointment
- **Endpoint**: `POST /api/appointments/6/complete/`
- **Response (`200 OK`)**:
```json
{
  "message": "Appointment marked as completed successfully.",
  "appointment": {
    "id": 6,
    "customer_name": "Kavya Menon",
    "status": "completed",
    "updated_at": "2026-10-18T17:38:50.000000Z"
  }
}
```

### G. Delete Appointment
- **Endpoint**: `DELETE /api/appointments/6/`
- **Response (`204 No Content`)**: Empty response body.

---

## 8. Error Handling & Validation Rules

| Scenario | HTTP Status | Response Payload Example |
| :--- | :--- | :--- |
| **Past Date/Time** | `400 Bad Request` | `{"appointment_date": ["Appointments cannot be scheduled in the past. Please select a future date and time."]}` |
| **Slot Already Booked** | `400 Bad Request` | `{"appointment_time": ["The slot on 2026-10-25 at 10:00 is already booked. Please choose another time slot."]}` |
| **Missing Required Field** | `400 Bad Request` | `{"customer_name": ["This field is required."], "email": ["This field is required."]}` |
| **Invalid Email Format** | `400 Bad Request` | `{"email": ["Enter a valid email address."]}` |
| **Rescheduling Cancelled Booking** | `400 Bad Request` | `{"error": ["A cancelled appointment cannot be modified or rescheduled."]}` |
| **Rescheduling Completed Booking** | `400 Bad Request` | `{"error": ["A completed appointment cannot be modified or rescheduled."]}` |
| **Repeated Cancellation** | `400 Bad Request` | `{"error": "This appointment has already been cancelled."}` |
| **Cancelling Completed Booking** | `400 Bad Request` | `{"error": "A completed appointment cannot be cancelled."}` |
| **Nonexistent ID** | `404 Not Found` | `{"detail": "No Appointment matches the given query."}` |
| **Unsupported Method (e.g. PUT)** | `405 Method Not Allowed` | `{"detail": "Method \"PUT\" not allowed."}` |
| **Malformed JSON** | `400 Bad Request` | `{"detail": "JSON parse error - Expecting property name enclosed in double quotes..."}` |

---

## 9. Automated Testing

The automated test suite uses Django REST Framework's `APITestCase` to test all functional requirements and edge cases.

### Running the Tests
```powershell
python manage.py test bookings --verbosity=2
```

### Verified Test Cases Summary (18 Tests)
1. `test_successful_appointment_booking`: Creates appointment with future date/time, returns 201 Created and default status `booked`.
2. `test_missing_required_fields`: Asserts 400 Bad Request when customer details or schedule are missing.
3. `test_invalid_email`: Validates email syntax, asserting 400 Bad Request.
4. `test_booking_in_the_past`: Asserts 400 Bad Request when date is in the past.
5. `test_listing_appointments`: Tests GET list, filtering by `status`, and searching by customer name.
6. `test_retrieving_a_booking`: Tests GET by ID, verifying response payload.
7. `test_nonexistent_appointment_id`: Asserts 404 Not Found for non-existent IDs.
8. `test_successful_rescheduling`: Patches new date and time, confirming database persistence.
9. `test_rescheduling_a_cancelled_appointment`: Prevents updating appointments that have been cancelled.
10. `test_rescheduling_a_completed_appointment`: Prevents updating appointments marked as completed.
11. `test_cancelling_an_appointment`: Transitions status to `cancelled` and rejects duplicate cancellation.
12. `test_completing_an_appointment`: Transitions status to `completed` and prevents invalid state changes.
13. `test_duplicate_time_slot_prevention`: Prevents two active bookings for the same date and time.
14. `test_booking_a_cancelled_appointment_released_slot`: Confirms that cancelled slots can be rebooked.
15. `test_successful_deletion`: Deletes booking and returns 204 No Content.
16. `test_method_not_allowed_on_put`: Confirms PUT returns 405 Method Not Allowed.
17. `test_malformed_json_request`: Confirms 400 Bad Request on invalid JSON syntax.
18. `test_database_unique_constraint`: Confirms SQLite database-level integrity error if serializer is bypassed.

---

## 10. Postman Testing Guide

A complete Postman collection is included in the project root: `postman_collection.json`.

### How to Import and Use in Postman
1. Open the **Postman** desktop application or web interface.
2. Click the **Import** button in the top-left corner.
3. Select or drag-and-drop `appointment_booking/postman_collection.json`.
4. You will see the collection named **"Appointment Booking Management System API"**.
5. The collection includes two pre-configured collection variables:
   - `base_url`: `http://127.0.0.1:8000`
   - `appointment_id`: `7`
6. Click through each request in the collection and hit **Send** to observe the responses.

---

## 11. Code Explanation: Important Files

- **`manage.py`**: Django's CLI entry point used for running tests, migrations, and starting the server.
- **`config/settings.py`**: Project settings. Registers `rest_framework`, `django_filters`, and `bookings.apps.BookingsConfig`. Configures default filter backends, JSON renderers, and SQLite database settings.
- **`config/urls.py`**: Top-level URL routing. Routes root `/` to a project overview and `/api/` to the bookings application routes.
- **`bookings/models.py`**: Contains the `Appointment` model with `AppointmentStatus` choices (`booked`, `completed`, `cancelled`), audit timestamps, helper methods (`is_in_past`), and a database-level `UniqueConstraint` on active slots.
- **`bookings/serializers.py`**: Serializes model instances to/from JSON. Implements custom validation ensuring non-blank customer names, preventing past booking dates, and catching slot collisions before saving.
- **`bookings/views.py`**: Contains `AppointmentViewSet` using DRF `ModelViewSet`. Implements custom actions (`@action`) for `cancel` and `complete` with strict state-transition guards.
- **`bookings/urls.py`**: Defines the DRF `DefaultRouter` which automatically wires standard REST routes (`/api/appointments/`, `/api/appointments/<id>/`, `/cancel/`, `/complete/`).
- **`bookings/admin.py`**: Configures the Django Admin interface with search fields, list filters, date hierarchy, and readable fieldsets.
- **`bookings/tests.py`**: Comprehensive 18-case test suite using DRF `APITestCase`.

---

## 12. Project Demonstration Script (Viva / Presentation)

When presenting this project to an interviewer or evaluator:

1. **Introduction**:
   > *"I have built an Appointment Booking Management System backend using Python, Django, and Django REST Framework. It provides complete RESTful endpoints for booking, listing, retrieving, rescheduling, cancelling, and completing appointments with strict business rules."*

2. **Database & Architecture**:
   > *"The database uses SQLite with an `Appointment` model. To prevent double-booking, I implemented a conditional database-level `UniqueConstraint` that ensures no two active appointments share the same date and time slot. When an appointment is cancelled, the slot is released automatically."*

3. **Validation & Business Logic**:
   > *"All inputs are validated in the serializer. The system rejects bookings in the past, ensures customer names are not blank, prevents modification of cancelled or completed appointments, and handles all errors with clean JSON error messages and proper HTTP status codes like 201, 204, 400, 404, and 405."*

4. **Demonstrating Tests**:
   > Run: `python manage.py test bookings --verbosity=2`
   > *"As you can see, all 18 automated tests pass, covering slot conflict prevention, state immutability, date validation, and CRUD operations."*

5. **Live API Execution**:
   > Open Postman or run `Invoke-RestMethod` to show:
   > - Creating an appointment (`POST /api/appointments/`) -> `201 Created`
   > - Trying to book the same slot -> `400 Bad Request (Slot already booked)`
   > - Cancelling it (`POST /api/appointments/<id>/cancel/`) -> `200 OK`
   > - Booking the newly freed slot -> `201 Created`

---

## 13. Internship Viva Questions & Answers

### Q1: Why did you choose Django REST Framework (DRF) for this project?
**Answer**: DRF provides powerful features for rapid and reliable API development: ModelSerializers for validation and data transformation, ViewSets and Routers for standardized REST URLs, built-in support for filtering and searching, and standardized HTTP status code handling.

### Q2: How did you implement slot-conflict prevention?
**Answer**: I implemented a two-tier defense:
1. **Serializer Level (`validate`)**: Before hitting the database, the serializer queries active appointments (`status__in=['booked', 'completed']`) for the requested date and time. If a match exists (excluding the current instance during rescheduling), it raises a DRF `ValidationError` with HTTP 400.
2. **Database Level (`UniqueConstraint`)**: In `Appointment.Meta`, a partial `UniqueConstraint` is declared with condition `status__in=['booked', 'completed']`. Even in case of concurrent requests or race conditions, the database engine enforces data integrity.

### Q3: Why can cancelled appointments have their slot rebooked, but completed appointments cannot?
**Answer**: When an appointment is cancelled, the customer will not be attending, so the slot is released to avoid lost capacity. When an appointment is completed, the service was already rendered at that date and time, so the historical record must be preserved and that past slot should not be overwritten.

### Q4: Why use PATCH instead of PUT for rescheduling?
**Answer**: `PUT` represents a full replacement of the entire resource requiring all fields to be supplied. `PATCH` represents a partial update, allowing the client to send only the modified fields (such as `appointment_date` and `appointment_time`) without resending all customer details.

### Q5: How are timezone and past-date validations handled?
**Answer**: With `USE_TZ = True` enabled in `settings.py`, the appointment date and time are combined into a datetime object and converted to timezone-aware UTC datetime. This is compared against `timezone.now()` to ensure no bookings or reschedules occur in the past.
