# Smart Volunteer Connect — Flask + PostgreSQL Full-Stack Platform

A production-grade full-stack platform connecting non-governmental organizations (NGOs) with passionate volunteers across India.

Built with **Python + Flask**, **PostgreSQL**, **SQLAlchemy ORM**, **Flask-Migrate (Alembic)**, **JWT Authentication**, **Bcrypt**, and an interactive vanilla JS frontend with real-time analytics, dynamic search & filtering, live dashboards, and smart opportunity matching.

---

## 🏗️ System Architecture

```
Smart-Vlountee-Connect-/
├── app/
│   ├── __init__.py          # Flask application factory, CORS, JWT error handlers
│   ├── config.py            # Development, Production, Testing configs (PostgreSQL/SQLite)
│   ├── extensions.py        # SQLAlchemy, Migrate, JWT, Bcrypt, CORS, Mail
│   ├── models/              # Normalized relational database models
│   │   ├── volunteer.py     # Volunteers table, skills, bio, availability
│   │   ├── ngo.py           # NGOs table, registration number, causes, verification
│   │   ├── event.py         # Events table, dates, category, capacity, status
│   │   ├── enrollment.py    # Volunteer enrollments, attendance, certificates
│   │   ├── feedback.py      # Event reviews, ratings (1-5 stars)
│   │   └── contact.py       # Contact messages
│   ├── routes/              # Modular Flask Blueprints
│   │   ├── auth.py          # Register, login, current user (/api/auth/me), logout
│   │   ├── events.py        # CRUD, filtering, search, enroll, attendance roster
│   │   ├── volunteers.py    # Volunteer profile, enrollments, certificates, smart matches
│   │   ├── ngos.py          # NGO profile, public list, NGO events, analytics
│   │   ├── stats.py         # Platform metrics and chart analytics
│   │   └── contact.py       # Contact form submissions and listing
│   ├── services/            # Core business logic layer
│   │   ├── event_service.py # Query filtering, transaction-safe enrollment
│   │   ├── matching_service.py # Weighted smart volunteer matching algorithm
│   │   └── stats_service.py # Aggregated platform & demographic calculations
│   ├── schemas/             # Marshmallow input validation & serialization
│   │   ├── auth_schema.py
│   │   ├── event_schema.py
│   │   ├── volunteer_schema.py
│   │   └── ngo_schema.py
│   ├── utils/               # Decorators & security helpers
│   │   ├── decorators.py    # @role_required('volunteer' | 'ngo')
│   │   └── security.py      # Password & email validation
│   └── static/              # Connected frontend assets served by Flask
│       ├── index.html
│       ├── style.css
│       └── app.js
├── migrations/              # Alembic database migration scripts
├── tests/                   # Pytest automated test suite (33 passing tests)
│   ├── conftest.py          # Test app & DB fixtures
│   ├── test_auth.py         # Registration, login, password hashing, tokens
│   ├── test_events.py       # CRUD, filters, search, ownership permissions
│   ├── test_enrollment.py   # Capacity checks, duplicates, unenrollment
│   ├── test_attendance_and_certificates.py # NGO attendance & certificates
│   ├── test_feedback.py     # Ratings, attendance validation
│   ├── test_dashboards_and_stats.py        # Metrics calculations
│   └── test_security_and_contact.py        # Tokens, role segregation
├── .env.example             # Safe environment template
├── requirements.txt         # Pinned production dependencies
├── pytest.ini               # Pytest path configuration
├── seed_db.py               # Comprehensive database seeder
├── run.py                   # Server entrypoint
└── README.md                # Documentation
```

---

## 🗄️ Normalized PostgreSQL Schema

| Table | Primary Key | Foreign Keys & Constraints | Key Columns |
| :--- | :--- | :--- | :--- |
| `volunteers` | `id` (SERIAL) | `email` (UNIQUE, INDEX) | `name`, `email`, `password_hash`, `phone`, `city`, `interests`, `availability`, `total_hours`, `is_active`, `created_at` |
| `ngos` | `id` (SERIAL) | `email` (UNIQUE, INDEX), `registration_number` (UNIQUE) | `name`, `email`, `password_hash`, `registration_number`, `city`, `state`, `cause_areas`, `verified`, `is_active` |
| `events` | `id` (SERIAL) | `ngo_id` -> `ngos.id` (INDEX) | `title`, `description`, `category`, `city` (INDEX), `venue`, `event_date`, `duration_hours`, `max_volunteers`, `status` |
| `enrollments` | `id` (SERIAL) | `volunteer_id` -> `volunteers.id`, `event_id` -> `events.id`, UNIQUE(`volunteer_id`, `event_id`) | `enrolled_at`, `attended` (BOOL), `hours_logged`, `certificate_issued`, `certificate_url` |
| `feedback` | `id` (SERIAL) | `volunteer_id` -> `volunteers.id`, `event_id` -> `events.id`, CHECK(`rating` BETWEEN 1 AND 5), UNIQUE(`volunteer_id`, `event_id`) | `rating`, `review_text`, `created_at` |
| `contact_messages` | `id` (SERIAL) | None | `name`, `email`, `subject`, `message`, `is_read`, `created_at` |

---

## 🚀 Quick Setup Guide

### 1. Prerequisites
- Python 3.10+ (tested on Python 3.14)
- PostgreSQL 14+ (or a free cloud database on [Neon](https://neon.tech) / [Supabase](https://supabase.com))

### 2. Create the PostgreSQL Database

**Using `psql` or PostgreSQL Command Line:**
```sql
CREATE DATABASE smart_volunteer_connect;
```

Or using command-line:
```bash
createdb smart_volunteer_connect
```

### 3. Clone Repository & Setup Virtual Environment

```bash
git clone https://github.com/Dev-Shubhangi-17/Smart-Vlountee-Connect-.git
cd Smart-Vlountee-Connect-

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Windows (CMD):
venv\Scripts\activate.bat
# Linux / macOS:
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Copy `.env.example` to `.env`:
```bash
# Windows:
copy .env.example .env
# Linux / macOS:
cp .env.example .env
```

Edit `.env` with your PostgreSQL database URI:
```ini
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=smart-volunteer-connect-secret-key-32chars-min
JWT_SECRET_KEY=smart-volunteer-connect-jwt-secret-key-32bytes-min
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/smart_volunteer_connect
FRONTEND_ORIGIN=http://localhost:5000
```
> **Note:** If you want to test immediately without configuring a local PostgreSQL service, simply leave `DATABASE_URL` unset or commented out — the application will automatically fall back to SQLite for instant local development.

### 6. Run Database Migrations

Apply database migrations:
```bash
flask db upgrade
```

### 7. Seed Demonstration Data

Populate the database with pre-configured NGOs, volunteers, events, enrollments, certificates, and reviews:
```bash
python seed_db.py
```

### 8. Start the Server

```bash
python run.py
```

The application and frontend will be live at:
**`http://localhost:5000`** 🚀

---

## 🔑 Pre-Seeded Demonstration Accounts

For instant testing through the frontend Login Modal or API:

| Role | Email | Password | Details |
| :--- | :--- | :--- | :--- |
| **Volunteer** | `riya@example.com` | `password123` | Riya Sharma — Mumbai, 4.0 hours logged, 1 certificate |
| **Volunteer** | `arjun@example.com` | `password123` | Arjun Mehta — Delhi, 5.0 hours logged, 1 certificate |
| **NGO Partner** | `contact@greenindia.org` | `password123` | GreenIndia Foundation — Verified NGO, Mumbai |
| **NGO Partner** | `info@lifesaverstrust.org` | `password123` | LifeSavers Trust — Verified NGO, Delhi |
| **NGO Partner** | `hello@edureach.org` | `password123` | EduReach India — Verified NGO, Mumbai |

*(The frontend Login Modal includes a **1-Click Fill Demo Credentials** button for easy testing.)*

---

## 🧪 Automated Testing

Automated tests run against an isolated in-memory test database using `pytest`:

```bash
pytest -v
```

### Test Coverage Highlights (33 Tests):
- ✅ Volunteer and NGO registration with password hashing (Bcrypt)
- ✅ Input validation (invalid emails, passwords < 6 characters, missing fields)
- ✅ Duplicate email and registration number prevention (409 Conflict)
- ✅ Login and JWT issuance with role claims
- ✅ Current user identity retrieval (`GET /api/auth/me`)
- ✅ Protected routes and role-based authorization (`@role_required`)
- ✅ Event CRUD operations and soft-cancellation
- ✅ Search, city filtering, category filtering, and date queries
- ✅ Transaction-safe enrollment and capacity overflow prevention
- ✅ Preventing duplicate enrollment and past event enrollment
- ✅ Volunteer un-enrollment (preventing un-enrollment after attendance)
- ✅ NGO viewing enrolled volunteers (`GET /api/events/<id>/enrollments`)
- ✅ NGO recording attendance, hours, and digital certificates
- ✅ Post-event feedback (1-5 star ratings, duplicate prevention, attendance verification)
- ✅ Platform-wide metrics and demographic calculations (empty & populated DB)
- ✅ Tampered and expired JWT token rejection

---

## 📡 REST API Reference

Base URL: `http://localhost:5000/api`

### 1. Authentication

| Method | Endpoint | Auth | Request Body | Description |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/auth/volunteer/register` | None | `{ name, email, password, phone, city, interests, availability }` | Register volunteer |
| `POST` | `/auth/volunteer/login` | None | `{ email, password }` | Volunteer login -> returns JWT |
| `POST` | `/auth/ngo/register` | None | `{ name, email, password, registration_number, city, cause_areas }` | Register NGO |
| `POST` | `/auth/ngo/login` | None | `{ email, password }` | NGO login -> returns JWT |
| `GET` | `/auth/me` | Bearer JWT | None | Current authenticated user & role |
| `POST` | `/auth/logout` | None | None | Client-side logout confirmation |

### 2. Events & Opportunities

| Method | Endpoint | Auth | Query / Body | Description |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/events` | None | `?search=...&city=...&category=...&page=1` | List & filter opportunities |
| `GET` | `/events/<id>` | None | None | Get event details |
| `POST` | `/events` | NGO JWT | `{ title, category, city, venue, event_date, duration_hours, max_volunteers }` | Create opportunity |
| `PUT` | `/events/<id>` | NGO JWT (Owner) | `{ title, venue, max_volunteers, ... }` | Update opportunity |
| `DELETE` | `/events/<id>` | NGO JWT (Owner) | None | Cancel opportunity |
| `POST` | `/events/<id>/enroll` | Volunteer JWT | None | Enroll in opportunity |
| `DELETE` | `/events/<id>/enroll` | Volunteer JWT | None | Cancel enrollment |
| `GET` | `/events/<id>/enrollments` | NGO JWT (Owner) | None | View volunteer roster |
| `POST` | `/events/<id>/attendance` | NGO JWT (Owner) | `{ enrollment_id, attended, hours_logged, certificate_issued }` | Record volunteer attendance |
| `GET` | `/events/<id>/feedback` | None | None | Event reviews & average rating |
| `POST` | `/events/<id>/feedback` | Volunteer JWT | `{ rating (1-5), review_text }` | Submit post-event review |

### 3. Volunteer Profile & Personal Dashboard

| Method | Endpoint | Auth | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/volunteers/me` | Volunteer JWT | Get personal profile |
| `PUT` | `/volunteers/me` | Volunteer JWT | Update profile details |
| `GET` | `/volunteers/me/enrollments` | Volunteer JWT | My enrolled opportunities (`?status=upcoming|past|attended`) |
| `GET` | `/volunteers/me/certificates` | Volunteer JWT | My verified digital certificates |
| `GET` | `/volunteers/me/stats` | Volunteer JWT | Personal dashboard metrics (hours, events, certificates) |
| `GET` | `/volunteers/me/matches` | Volunteer JWT | Algorithmic smart matches based on city and causes |

### 4. NGO Profile & Analytics

| Method | Endpoint | Auth | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/ngos` | None | List verified NGOs (`?city=...&cause_area=...`) |
| `GET` | `/ngos/<id>` | None | NGO details and bio |
| `GET` | `/ngos/<id>/events` | None | Public events of an NGO |
| `GET` | `/ngos/me` | NGO JWT | Get own NGO profile |
| `PUT` | `/ngos/me` | NGO JWT | Update NGO profile |
| `GET` | `/ngos/me/events` | NGO JWT | Get all managed events |
| `GET` | `/ngos/me/stats` | NGO JWT | NGO analytics (volunteers, hours contributed, ratings) |

### 5. Platform Stats & Contact

| Method | Endpoint | Auth | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/stats` | None | Aggregated platform numbers (volunteers, NGOs, events, hours) |
| `GET` | `/stats/analytics` | None | Demographic breakdowns & cause distribution |
| `POST` | `/contact` | None | Submit contact form `{ name, email, subject, message }` |
| `GET` | `/contact` | None | View submitted inquiries |
| `GET` | `/health` | None | Health check endpoint |

---

## 🔒 Security Best Practices Implemented

1. **Password Security:** All passwords hashed with industry-standard **Bcrypt** with unique salt. Plaintext passwords are never logged or stored.
2. **Stateless JWT Authorization:** Tokens signed using HMAC-SHA256 with cryptographic secret keys >= 32 characters.
3. **Role Segregation:** Server-side claim validation ensures volunteers cannot access NGO management routes, and NGOs cannot enroll as volunteers.
4. **Ownership Verification:** NGOs can only edit, cancel, and access rosters for events they created.
5. **Database Transaction Safety:** Unique constraints and atomic SQLAlchemy transactions prevent race conditions during enrollment and feedback submission.
6. **SQL Injection Protection:** Queries execute through parameterized SQLAlchemy ORM statements.
7. **CORS:** Configurable frontend origin headers preventing cross-origin exploitation.

---

## 🌐 Deployment to Production (e.g. Render / Heroku / AWS)

1. Connect your GitHub repository to Render / Heroku.
2. Set Build Command:
   ```bash
   pip install -r requirements.txt && flask db upgrade
   ```
3. Set Start Command:
   ```bash
   gunicorn run:app
   ```
4. Configure environment variables in the host dashboard:
   - `DATABASE_URL`: Your production PostgreSQL connection string
   - `SECRET_KEY`: A randomly generated 64-character secret
   - `JWT_SECRET_KEY`: A randomly generated 64-character secret
   - `FRONTEND_ORIGIN`: Your production frontend domain

---

## 👥 Author & Contributions

- **Author & Maintainer:** [Dev-Shubhangi-17](https://github.com/Dev-Shubhangi-17)
- **Project:** Smart Volunteer Connect
- **License:** MIT License
