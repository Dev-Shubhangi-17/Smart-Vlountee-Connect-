# Smart Volunteer Connect — Flask + PostgreSQL Backend

A complete REST API backend for the [Smart Volunteer Connect](https://yashmajmudar-33.github.io/Smart-Vlountee-Connect-/) platform — connecting NGOs with passionate volunteers across India.

---

## 🚀 Quick Start

### 1. Clone & Navigate
```bash
cd smart-volunteer-connect-backend
```

### 2. Create Virtual Environment
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Copy `.env.example` to `.env` and fill in your values:
```bash
copy .env.example .env
```

**Getting your Supabase DATABASE_URL:**
1. Go to [supabase.com](https://supabase.com) → Create a project
2. Go to **Settings** → **Database** → **Connection String**
3. Choose **URI** tab and copy the connection string
4. Replace `[YOUR-PASSWORD]` with your database password
5. Paste it as `DATABASE_URL` in your `.env` file

### 5. Run Database Migrations
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 6. Start the Server
```bash
python run.py
```

The API will be running at `http://localhost:5000` ✅

---

## 📋 API Reference

### Base URL
- **Local**: `http://localhost:5000/api`
- **Health Check**: `GET /api/health`

---

### 🔐 Authentication

All protected routes require a Bearer token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

#### Register Volunteer
```
POST /api/auth/volunteer/register
```
```json
{
  "name": "Riya Sharma",
  "email": "riya@example.com",
  "password": "securepassword",
  "phone": "9876543210",
  "city": "Mumbai",
  "interests": ["Education", "Healthcare", "Environment"],
  "availability": "Weekends"
}
```

#### Volunteer Login
```
POST /api/auth/volunteer/login
```
```json
{
  "email": "riya@example.com",
  "password": "securepassword"
}
```

#### Register NGO
```
POST /api/auth/ngo/register
```
```json
{
  "name": "Teach For India",
  "email": "contact@teachforindia.org",
  "password": "securepassword",
  "registration_number": "MH/NGO/12345",
  "city": "Mumbai",
  "cause_areas": ["Education", "Youth Development"],
  "description": "We place talented graduates as full-time teachers in under-resourced schools."
}
```

#### NGO Login
```
POST /api/auth/ngo/login
```

---

### 👤 Volunteer Endpoints

| Method | Route | Auth | Description |
|--------|-------|------|-------------|
| GET | `/api/volunteers/me` | Volunteer JWT | Get own profile |
| PUT | `/api/volunteers/me` | Volunteer JWT | Update profile |
| GET | `/api/volunteers/me/enrollments` | Volunteer JWT | My enrolled events |
| GET | `/api/volunteers/me/certificates` | Volunteer JWT | My certificates |
| GET | `/api/volunteers/me/stats` | Volunteer JWT | Dashboard stats |
| GET | `/api/volunteers/me/matches` | Volunteer JWT | Smart-matched events |

**Query params for `/me/enrollments`:**
- `?status=upcoming` — only future events
- `?status=past` — only past events
- `?status=attended` — only attended events

---

### 🏢 NGO Endpoints

| Method | Route | Auth | Description |
|--------|-------|------|-------------|
| GET | `/api/ngos` | None | List all NGOs |
| GET | `/api/ngos/<id>` | None | Get NGO detail |
| GET | `/api/ngos/<id>/events` | None | NGO's events |
| GET | `/api/ngos/me` | NGO JWT | Own profile |
| PUT | `/api/ngos/me` | NGO JWT | Update profile |
| GET | `/api/ngos/me/events` | NGO JWT | Own events |
| GET | `/api/ngos/me/stats` | NGO JWT | Analytics dashboard |

**Query params for `GET /api/ngos`:**
- `?city=Mumbai` — filter by city
- `?cause_area=Education` — filter by cause
- `?search=teach` — search by name

---

### 📅 Event Endpoints

| Method | Route | Auth | Description |
|--------|-------|------|-------------|
| GET | `/api/events` | None | List events |
| GET | `/api/events/<id>` | None | Event detail |
| POST | `/api/events` | NGO JWT | Create event |
| PUT | `/api/events/<id>` | NGO JWT | Update event |
| DELETE | `/api/events/<id>` | NGO JWT | Cancel event |
| POST | `/api/events/<id>/enroll` | Volunteer JWT | Enroll |
| DELETE | `/api/events/<id>/enroll` | Volunteer JWT | Un-enroll |
| GET | `/api/events/<id>/feedback` | None | Event reviews |
| POST | `/api/events/<id>/feedback` | Volunteer JWT | Submit review |

**Create Event body:**
```json
{
  "title": "Tree Plantation Drive",
  "event_date": "2026-09-15",
  "start_time": "09:00",
  "duration_hours": 4,
  "category": "Environment",
  "city": "Mumbai",
  "venue": "Aarey Colony, Mumbai",
  "description": "Join us to plant 500 trees in Aarey forest.",
  "max_volunteers": 50
}
```

**Query params for `GET /api/events`:**
- `?city=Mumbai`
- `?category=Environment`
- `?search=plantation`
- `?date_from=2026-09-01&date_to=2026-12-31`
- `?page=1&per_page=12`

---

### 📊 Stats
```
GET /api/stats
```
Returns platform-wide numbers for the homepage counters.

---

### 📬 Contact
```
POST /api/contact
```
```json
{
  "name": "Arjun Mehta",
  "email": "arjun@example.com",
  "subject": "Partnership Enquiry",
  "message": "We'd love to partner with your platform..."
}
```

---

## 🗄️ Database Schema

```
volunteers          — id, name, email, password_hash, phone, city, bio, interests, availability
ngos                — id, name, email, password_hash, registration_number, city, state, cause_areas, verified
events              — id, ngo_id, title, description, category, city, venue, event_date, max_volunteers, status
enrollments         — id, volunteer_id, event_id, attended, hours_logged, certificate_issued
feedback            — id, volunteer_id, event_id, rating (1-5), review_text
contact_messages    — id, name, email, subject, message
```

---

## 🔗 Connecting the Frontend

To connect your GitHub Pages frontend to this backend, add this to your `index.html` (or a new `api.js` file):

```javascript
const API_BASE = "http://localhost:5000/api"; // Change to your deployed URL

// Example: Volunteer Registration
async function registerVolunteer(formData) {
  const res = await fetch(`${API_BASE}/auth/volunteer/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(formData)
  });
  const data = await res.json();
  if (res.ok) {
    localStorage.setItem("token", data.access_token);
    alert("Registered successfully!");
  } else {
    alert("Error: " + data.error);
  }
}

// Example: Load Events
async function loadEvents(city = "", category = "") {
  const res = await fetch(`${API_BASE}/events?city=${city}&category=${category}`);
  const data = await res.json();
  return data.events;
}

// Example: Enroll in Event (volunteer must be logged in)
async function enrollInEvent(eventId) {
  const token = localStorage.getItem("token");
  const res = await fetch(`${API_BASE}/events/${eventId}/enroll`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`
    }
  });
  const data = await res.json();
  alert(data.message || data.error);
}

// Example: Platform Stats for Hero Section
async function loadPlatformStats() {
  const res = await fetch(`${API_BASE}/stats`);
  const data = await res.json();
  document.querySelector(".volunteers-count").textContent = data.total_volunteers + "+";
  document.querySelector(".ngo-count").textContent = data.total_ngos + "+";
  document.querySelector(".events-count").textContent = data.total_events + "+";
}
```

---

## 🚢 Deploying to Render (Free)

1. Push this folder to a GitHub repository
2. Go to [render.com](https://render.com) → New Web Service
3. Connect your repo
4. Set:
   - **Build Command**: `pip install -r requirements.txt && flask db upgrade`
   - **Start Command**: `gunicorn run:app`
5. Add all your `.env` variables in **Environment** settings
6. Update `FRONTEND_ORIGIN` to `https://yashmajmudar-33.github.io`

---

## 📁 Project Structure

```
smart-volunteer-connect-backend/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── config.py            # Dev/Prod/Test configs
│   ├── extensions.py        # db, jwt, bcrypt, cors, mail
│   ├── models/
│   │   ├── __init__.py
│   │   ├── volunteer.py
│   │   ├── ngo.py
│   │   ├── event.py
│   │   ├── enrollment.py
│   │   ├── feedback.py
│   │   └── contact.py
│   └── routes/
│       ├── __init__.py
│       ├── auth.py
│       ├── volunteers.py
│       ├── ngos.py
│       ├── events.py
│       ├── stats.py
│       └── contact.py
├── migrations/
├── .env.example
├── requirements.txt
├── run.py
└── README.md
```
