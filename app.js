// Smart Volunteer Connect — Centralized Frontend API Client & Application Logic

const API_BASE_URL = (
  window.location.origin.includes('localhost') || 
  window.location.origin.includes('127.0.0.1') ||
  window.location.protocol === 'file:'
) ? 'http://localhost:5000' : '';

// ------------------------------------------------------------
// Centralized API Client with Auth Header and Error Handling
// ------------------------------------------------------------
const api = {
  getToken() {
    return localStorage.getItem('svc_token');
  },
  setToken(token) {
    if (token) localStorage.setItem('svc_token', token);
    else localStorage.removeItem('svc_token');
  },
  getUser() {
    try {
      return JSON.parse(localStorage.getItem('svc_user') || 'null');
    } catch {
      return null;
    }
  },
  setUser(user) {
    if (user) localStorage.setItem('svc_user', JSON.stringify(user));
    else localStorage.removeItem('svc_user');
  },
  getRole() {
    return localStorage.getItem('svc_role');
  },
  setRole(role) {
    if (role) localStorage.setItem('svc_role', role);
    else localStorage.removeItem('svc_role');
  },
  clearAuth() {
    localStorage.removeItem('svc_token');
    localStorage.removeItem('svc_user');
    localStorage.removeItem('svc_role');
  },
  async request(endpoint, options = {}) {
    const url = endpoint.startsWith('http') ? endpoint : `${API_BASE_URL}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      ...(options.headers || {})
    };

    const token = this.getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers
      });

      if (response.status === 401 && token) {
        // Token expired or invalid — clear state
        console.warn('Session expired. Logging out.');
        this.clearAuth();
        updateNavAuthState(null);
      }

      let data = {};
      try {
        data = await response.json();
      } catch (e) {
        data = { error: response.ok ? '' : `Server returned error (${response.status} ${response.statusText || ''})`.trim() };
      }
      return { ok: response.ok, status: response.status, data };
    } catch (err) {
      console.error(`API Error [${endpoint}]:`, err);
      return { ok: false, status: 0, data: { error: 'Could not connect to backend server. Make sure Flask is running on http://localhost:5000' } };
    }
  }
};

let currentUser = null;
let currentRole = null;
let userEnrolledEventIds = new Set();
let eventSearchTimer = null;

// ------------------------------------------------------------
// Initialization
// ------------------------------------------------------------
document.addEventListener('DOMContentLoaded', async function() {
  initModals();
  initForms();
  initFilters();

  await checkAuthState();
  loadLiveStats();
  loadUpcomingEvents();
});

// ------------------------------------------------------------
// Authentication State Management
// ------------------------------------------------------------
async function checkAuthState() {
  const token = api.getToken();
  if (!token) {
    currentUser = null;
    currentRole = null;
    userEnrolledEventIds.clear();
    updateNavAuthState(null);
    hydrateDashboards();
    return;
  }

  const { ok, data } = await api.request('/api/auth/me');
  if (ok && data.user) {
    currentUser = data.user;
    currentRole = data.role;
    api.setUser(data.user);
    api.setRole(data.role);
    updateNavAuthState(data);

    if (currentRole === 'volunteer') {
      await loadUserEnrollmentIds();
    }
    hydrateDashboards();
  } else {
    api.clearAuth();
    currentUser = null;
    currentRole = null;
    userEnrolledEventIds.clear();
    updateNavAuthState(null);
    hydrateDashboards();
  }
}

function updateNavAuthState(authData) {
  const guestCta = document.getElementById('navGuestCta');
  const userBadge = document.getElementById('navUserBadge');
  const userNameEl = document.getElementById('navUserName');
  const userRoleEl = document.getElementById('navUserRole');

  if (authData && authData.user) {
    if (guestCta) guestCta.style.display = 'none';
    if (userBadge) {
      userBadge.style.display = 'flex';
      userNameEl.textContent = authData.user.name || 'Account';
      userRoleEl.textContent = authData.role === 'ngo' ? 'NGO Partner' : 'Volunteer';
    }
  } else {
    if (guestCta) guestCta.style.display = 'flex';
    if (userBadge) userBadge.style.display = 'none';
  }
}

async function loadUserEnrollmentIds() {
  if (currentRole !== 'volunteer') return;
  const { ok, data } = await api.request('/api/volunteers/me/enrollments');
  if (ok && data.enrollments) {
    userEnrolledEventIds = new Set(data.enrollments.map(e => e.event_id));
  }
}

// ------------------------------------------------------------
// Modals Handling
// ------------------------------------------------------------
function initModals() {
  const loginModal = document.getElementById('loginModal');
  const openLoginBtns = document.querySelectorAll('.open-login-btn, #navLoginBtn');
  const closeLoginBtn = document.getElementById('closeLoginModal');

  openLoginBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const targetRole = btn.getAttribute('data-role') || 'volunteer';
      switchLoginTab(targetRole);
      loginModal?.classList.add('active');
    });
  });

  closeLoginBtn?.addEventListener('click', () => {
    loginModal?.classList.remove('active');
  });

  // Tab switching inside Login Modal
  const tabVol = document.getElementById('tabLoginVol');
  const tabNGO = document.getElementById('tabLoginNGO');
  const loginRoleInput = document.getElementById('login_role');
  const quickCredsText = document.getElementById('quickCredsText');

  tabVol?.addEventListener('click', () => switchLoginTab('volunteer'));
  tabNGO?.addEventListener('click', () => switchLoginTab('ngo'));

  function switchLoginTab(role) {
    if (role === 'volunteer') {
      tabVol?.classList.add('active');
      tabNGO?.classList.remove('active');
      if (loginRoleInput) loginRoleInput.value = 'volunteer';
      if (quickCredsText) quickCredsText.innerHTML = 'Email: <code>riya@example.com</code> | Password: <code>password123</code>';
    } else {
      tabNGO?.classList.add('active');
      tabVol?.classList.remove('active');
      if (loginRoleInput) loginRoleInput.value = 'ngo';
      if (quickCredsText) quickCredsText.innerHTML = 'Email: <code>contact@greenindia.org</code> | Password: <code>password123</code>';
    }
  }

  // Quick fill demo credentials
  document.getElementById('fillDemoCredsBtn')?.addEventListener('click', () => {
    const role = loginRoleInput?.value || 'volunteer';
    const emailInput = document.getElementById('login_email');
    const passInput = document.getElementById('login_password');
    if (role === 'volunteer') {
      if (emailInput) emailInput.value = 'riya@example.com';
      if (passInput) passInput.value = 'password123';
    } else {
      if (emailInput) emailInput.value = 'contact@greenindia.org';
      if (passInput) passInput.value = 'password123';
    }
  });

  // Login Form Submission
  const loginForm = document.getElementById('loginForm');
  loginForm?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const role = loginRoleInput?.value || 'volunteer';
    const email = document.getElementById('login_email')?.value.trim();
    const password = document.getElementById('login_password')?.value;
    const submitBtn = document.getElementById('loginSubmitBtn');
    const originalText = submitBtn.innerHTML;

    if (!email || !password) {
      alert('Please enter both email and password.');
      return;
    }

    try {
      submitBtn.disabled = true;
      submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Signing in...';

      const endpoint = role === 'ngo' ? '/api/auth/ngo/login' : '/api/auth/volunteer/login';
      const { ok, data } = await api.request(endpoint, {
        method: 'POST',
        body: JSON.stringify({ email, password })
      });

      if (ok && data.access_token) {
        api.setToken(data.access_token);
        api.setUser(data.volunteer || data.ngo);
        api.setRole(role);
        loginModal?.classList.remove('active');
        loginForm.reset();
        alert(`✅ Welcome back, ${(data.volunteer || data.ngo).name}!`);
        await checkAuthState();
        loadUpcomingEvents();
        // Switch to corresponding dashboard tab
        if (role === 'volunteer') {
          const tabV = document.getElementById('tab-volunteer');
          if (tabV) tabV.checked = true;
        } else {
          const tabN = document.getElementById('tab-ngo');
          if (tabN) tabN.checked = true;
        }
      } else {
        alert(`❌ Login failed: ${data.error || 'Invalid credentials'}`);
      }
    } finally {
      submitBtn.disabled = false;
      submitBtn.innerHTML = originalText;
    }
  });

  // Logout Button
  document.getElementById('navLogoutBtn')?.addEventListener('click', async (e) => {
    e.preventDefault();
    await api.request('/api/auth/logout', { method: 'POST' });
    api.clearAuth();
    currentUser = null;
    currentRole = null;
    userEnrolledEventIds.clear();
    updateNavAuthState(null);
    hydrateDashboards();
    loadUpcomingEvents();
    alert('Logged out successfully.');
  });

  // Close modals when clicking backdrop
  window.addEventListener('click', (e) => {
    if (e.target.classList.contains('svc-modal-overlay')) {
      e.target.classList.remove('active');
    }
  });

  // Create Event Modal handlers (NGO only)
  const createEventModal = document.getElementById('createEventModal');
  document.getElementById('openCreateEventModalBtn')?.addEventListener('click', () => {
    if (currentRole !== 'ngo') {
      alert('Only registered NGOs can post events.');
      return;
    }
    createEventModal?.classList.add('active');
  });
  document.getElementById('closeCreateEventModal')?.addEventListener('click', () => {
    createEventModal?.classList.remove('active');
  });

  // Attendance Modal handlers
  document.getElementById('closeAttendanceModal')?.addEventListener('click', () => {
    document.getElementById('attendanceModal')?.classList.remove('active');
  });
}

// ------------------------------------------------------------
// Forms: Registration & Contact
// ------------------------------------------------------------
function initForms() {
  // Volunteer Registration Form
  const volunteerForm = document.getElementById('volunteerForm');
  if (volunteerForm) {
    volunteerForm.addEventListener('submit', async function(e) {
      e.preventDefault();

      const name = document.getElementById('vol_name')?.value.trim();
      const email = document.getElementById('vol_email')?.value.trim();
      const phone = document.getElementById('vol_phone')?.value.trim();
      const age = parseInt(document.getElementById('vol_age')?.value || '0');
      const occupation = document.getElementById('vol_occupation')?.value;
      const city = document.getElementById('vol_city')?.value.trim();
      const organization = document.getElementById('vol_organization')?.value.trim();
      const availability = document.getElementById('vol_availability')?.value;
      const password = document.getElementById('vol_password')?.value || 'password123';

      const interestCheckboxes = document.querySelectorAll('#volunteerForm .interest-chip-wrap input[type="checkbox"]:checked');
      const interests = Array.from(interestCheckboxes).map(cb => cb.nextElementSibling.textContent.replace(/^[^\w]+/, '').trim());

      if (!name || !email || !phone || !city) {
        alert('⚠️ Please fill in all required fields (Name, Email, Phone, Location)');
        return;
      }

      const payload = {
        name,
        email,
        password,
        phone,
        city,
        interests,
        availability,
        bio: `${occupation || 'Volunteer'} from ${city}`
      };

      const submitBtn = volunteerForm.querySelector('button[type="submit"]');
      const originalText = submitBtn.innerHTML;

      try {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Registering...';

        const { ok, data } = await api.request('/api/auth/volunteer/register', {
          method: 'POST',
          body: JSON.stringify(payload)
        });

        if (ok && data.volunteer) {
          alert(`✅ Registration successful! Welcome ${data.volunteer.name}. Your profile ID is #${data.volunteer.id}`);
          if (data.access_token) {
            api.setToken(data.access_token);
            api.setUser(data.volunteer);
            api.setRole('volunteer');
            await checkAuthState();
          }
          volunteerForm.reset();
          loadLiveStats();
          loadUpcomingEvents();
        } else {
          alert(`❌ Registration failed: ${data.error || 'Unknown error'}`);
        }
      } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
      }
    });
  }

  // NGO Registration Form
  const ngoForm = document.getElementById('ngoForm');
  if (ngoForm) {
    ngoForm.addEventListener('submit', async function(e) {
      e.preventDefault();

      const name = document.getElementById('ngo_name')?.value.trim();
      const registration_number = document.getElementById('ngo_reg_number')?.value.trim();
      const cause_areas = document.getElementById('ngo_focus')?.value;
      const contact_person = document.getElementById('ngo_contact_person')?.value.trim();
      const city = document.getElementById('ngo_city')?.value.trim();
      const email = document.getElementById('ngo_email')?.value.trim();
      const phone = document.getElementById('ngo_phone')?.value.trim();
      const description = document.getElementById('ngo_about')?.value.trim();
      const password = document.getElementById('ngo_password')?.value || 'password123';

      if (!name || !email || !phone || !city) {
        alert('⚠️ Please fill in all required fields');
        return;
      }

      const payload = {
        name,
        email,
        password,
        registration_number,
        phone,
        city,
        cause_areas: cause_areas ? [cause_areas] : [],
        description
      };

      const submitBtn = ngoForm.querySelector('button[type="submit"]');
      const originalText = submitBtn.innerHTML;

      try {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Registering...';

        const { ok, data } = await api.request('/api/auth/ngo/register', {
          method: 'POST',
          body: JSON.stringify(payload)
        });

        if (ok && data.ngo) {
          alert(`✅ NGO Registration successful! ${data.ngo.name} registered under ID #${data.ngo.id}`);
          if (data.access_token) {
            api.setToken(data.access_token);
            api.setUser(data.ngo);
            api.setRole('ngo');
            await checkAuthState();
          }
          ngoForm.reset();
          loadLiveStats();
          loadUpcomingEvents();
        } else {
          alert(`❌ Registration failed: ${data.error || 'Unknown error'}`);
        }
      } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
      }
    });
  }

  // NGO Create Event Form
  const createEventForm = document.getElementById('createEventForm');
  if (createEventForm) {
    createEventForm.addEventListener('submit', async function(e) {
      e.preventDefault();

      const title = document.getElementById('ce_title')?.value.trim();
      const category = document.getElementById('ce_category')?.value;
      const city = document.getElementById('ce_city')?.value.trim();
      const event_date = document.getElementById('ce_date')?.value;
      const start_time = document.getElementById('ce_time')?.value;
      const duration_hours = parseFloat(document.getElementById('ce_duration')?.value || '4');
      const max_volunteers = parseInt(document.getElementById('ce_capacity')?.value || '0') || null;
      const venue = document.getElementById('ce_venue')?.value.trim();
      const description = document.getElementById('ce_description')?.value.trim();

      if (!title || !event_date || !city) {
        alert('Please fill in required fields (Title, Date, City)');
        return;
      }

      const submitBtn = document.getElementById('ceSubmitBtn');
      const originalText = submitBtn.innerHTML;

      try {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Publishing...';

        const { ok, data } = await api.request('/api/events', {
          method: 'POST',
          body: JSON.stringify({
            title, category, city, event_date, start_time, duration_hours, max_volunteers, venue, description
          })
        });

        if (ok) {
          alert('✅ Event published successfully!');
          document.getElementById('createEventModal')?.classList.remove('active');
          createEventForm.reset();
          loadUpcomingEvents();
          hydrateNGOEvents();
        } else {
          alert(`❌ Failed to create event: ${data.error || 'Error'}`);
        }
      } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
      }
    });
  }

  // Contact Form
  const contactForm = document.getElementById('contactForm');
  if (contactForm) {
    contactForm.addEventListener('submit', async function(e) {
      e.preventDefault();

      const name = document.getElementById('contact_name')?.value.trim();
      const email = document.getElementById('contact_email')?.value.trim();
      const subject = document.getElementById('contact_subject')?.value;
      const message = document.getElementById('contact_message')?.value.trim();

      if (!name || !email || !message) {
        alert('⚠️ Please fill in Name, Email, and Message');
        return;
      }

      const payload = { name, email, subject, message };
      const submitBtn = contactForm.querySelector('button[type="submit"]');
      const originalText = submitBtn.innerHTML;

      try {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Sending...';

        const { ok, data } = await api.request('/api/contact', {
          method: 'POST',
          body: JSON.stringify(payload)
        });

        if (ok) {
          alert(`✅ ${data.message || 'Message sent successfully!'}`);
          contactForm.reset();
        } else {
          alert(`❌ Error: ${data.error || 'Failed to send message'}`);
        }
      } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
      }
    });
  }
}

// ------------------------------------------------------------
// Search & Filter Listeners for Events
// ------------------------------------------------------------
function initFilters() {
  const searchInput = document.getElementById('eventSearchInput');
  const catFilter = document.getElementById('eventCategoryFilter');
  const cityFilter = document.getElementById('eventCityFilter');

  const triggerSearch = () => {
    clearTimeout(eventSearchTimer);
    eventSearchTimer = setTimeout(() => {
      loadUpcomingEvents();
    }, 300);
  };

  searchInput?.addEventListener('input', triggerSearch);
  catFilter?.addEventListener('change', triggerSearch);
  cityFilter?.addEventListener('input', triggerSearch);
}

// ------------------------------------------------------------
// Live Stats & Platform Analytics
// ------------------------------------------------------------
async function loadLiveStats() {
  const { ok, data: stats } = await api.request('/api/stats');
  if (!ok) return;

  // Hero section counters
  const statNums = document.querySelectorAll('.hero-stat-num');
  if (statNums.length >= 3) {
    statNums[0].textContent = (stats.total_volunteers || 0) + '+';
    statNums[1].textContent = (stats.total_ngos || 0) + '+';
    statNums[2].textContent = (stats.total_events || 0) + '+';
  }

  // Analytics section counters
  const aVol = document.getElementById('analytics-total-vols');
  const aNGO = document.getElementById('analytics-total-ngos');
  const aEvents = document.getElementById('analytics-total-events');
  const aCerts = document.getElementById('analytics-total-certs');

  if (aVol) aVol.textContent = (stats.total_volunteers || 0).toLocaleString() + '+';
  if (aNGO) aNGO.textContent = (stats.total_ngos || 0).toLocaleString() + '+';
  if (aEvents) aEvents.textContent = (stats.total_events || 0).toLocaleString() + '+';
  if (aCerts) aCerts.textContent = (stats.total_certificates_issued || 0).toLocaleString() + '+';
}

// ------------------------------------------------------------
// Events Grid Rendering & Actions
// ------------------------------------------------------------
async function loadUpcomingEvents() {
  const eventsGrid = document.querySelector('.events-grid');
  if (!eventsGrid) return;

  const search = document.getElementById('eventSearchInput')?.value.trim() || '';
  const category = document.getElementById('eventCategoryFilter')?.value || '';
  const city = document.getElementById('eventCityFilter')?.value.trim() || '';

  const params = new URLSearchParams();
  if (search) params.append('search', search);
  if (category && category !== 'all') params.append('category', category);
  if (city) params.append('city', city);

  const endpoint = `/api/events?${params.toString()}`;
  const { ok, data } = await api.request(endpoint);

  if (!ok || !data.events || data.events.length === 0) {
    eventsGrid.innerHTML = `
      <div style="grid-column: 1 / -1; text-align: center; padding: 48px; color: var(--text-secondary);">
        <i class="fa-solid fa-calendar-xmark" style="font-size: 2.5rem; margin-bottom: 12px; color: var(--text-muted);"></i>
        <h3>No volunteer opportunities match your filter</h3>
        <p>Try searching for a different city, cause category, or keyword.</p>
      </div>
    `;
    return;
  }

  eventsGrid.innerHTML = data.events.map((evt, idx) => {
    const isEnrolled = userEnrolledEventIds.has(evt.id);
    const spotsLeft = evt.spots_left;
    const isFull = spotsLeft !== null && spotsLeft <= 0;

    let actionBtnHtml = '';
    if (currentRole === 'volunteer') {
      if (isEnrolled) {
        actionBtnHtml = `<button type="button" class="btn btn-outline btn-sm unenroll-btn" data-event-id="${evt.id}"><i class="fa-solid fa-check"></i> Enrolled (Cancel)</button>`;
      } else if (isFull) {
        actionBtnHtml = `<button type="button" class="btn btn-outline btn-sm" disabled>Full</button>`;
      } else {
        actionBtnHtml = `<button type="button" class="btn btn-primary btn-sm enroll-btn" data-event-id="${evt.id}"><i class="fa-solid fa-hand-holding-heart"></i> Enroll Now</button>`;
      }
    } else {
      actionBtnHtml = `<a href="#volunteer-reg" class="btn btn-primary btn-sm">Register</a>`;
    }

    return `
      <div class="glass-card event-card anim anim-d${(idx % 3) + 1}">
        <div class="event-image">${getCategoryEmoji(evt.category)}</div>
        <div class="event-body">
          <span class="event-category">${evt.category || 'General'}</span>
          <h3>${evt.title}</h3>
          <div class="event-meta">
            <div class="event-meta-item"><i class="fa-solid fa-building-ngo"></i> ${evt.ngo?.name || 'Verified NGO'}</div>
            <div class="event-meta-item"><i class="fa-solid fa-location-dot"></i> ${evt.venue || evt.city || 'India'}</div>
            <div class="event-meta-item"><i class="fa-solid fa-calendar"></i> ${formatDate(evt.event_date)} ${evt.start_time ? '· ' + evt.start_time : ''}</div>
          </div>
          <div class="event-footer">
            <div class="seats-badge">Seats: <span>${spotsLeft !== null ? spotsLeft + ' left' : 'Open'}</span></div>
            ${actionBtnHtml}
          </div>
        </div>
      </div>
    `;
  }).join('');

  // Attach event action handlers
  eventsGrid.querySelectorAll('.enroll-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
      const eventId = btn.getAttribute('data-event-id');
      await enrollInEvent(eventId);
    });
  });

  eventsGrid.querySelectorAll('.unenroll-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
      const eventId = btn.getAttribute('data-event-id');
      if (confirm('Are you sure you want to cancel your enrollment for this event?')) {
        await unenrollFromEvent(eventId);
      }
    });
  });
}

async function enrollInEvent(eventId) {
  if (currentRole !== 'volunteer') {
    alert('Please log in or register as a volunteer to enroll.');
    return;
  }

  const { ok, data } = await api.request(`/api/events/${eventId}/enroll`, { method: 'POST' });
  if (ok) {
    alert(`🎉 ${data.message || 'Enrolled successfully!'}`);
    userEnrolledEventIds.add(parseInt(eventId));
    loadUpcomingEvents();
    hydrateVolunteerDashboard();
  } else {
    alert(`❌ ${data.error || 'Could not enroll in this event'}`);
  }
}

async function unenrollFromEvent(eventId) {
  const { ok, data } = await api.request(`/api/events/${eventId}/enroll`, { method: 'DELETE' });
  if (ok) {
    alert(`✅ ${data.message || 'Un-enrolled successfully.'}`);
    userEnrolledEventIds.delete(parseInt(eventId));
    loadUpcomingEvents();
    hydrateVolunteerDashboard();
  } else {
    alert(`❌ ${data.error || 'Could not cancel enrollment'}`);
  }
}

// ------------------------------------------------------------
// Dashboards Hydration
// ------------------------------------------------------------
function hydrateDashboards() {
  hydrateVolunteerDashboard();
  hydrateNGODashboard();
}

async function hydrateVolunteerDashboard() {
  const authPrompt = document.getElementById('vol-auth-prompt');
  const extraSection = document.getElementById('vol-dash-extra');

  if (currentRole === 'volunteer' && currentUser) {
    if (authPrompt) authPrompt.style.display = 'none';
    if (extraSection) extraSection.style.display = 'block';

    const { ok, data: stats } = await api.request('/api/volunteers/me/stats');
    if (ok) {
      setText('vol-dash-registered', stats.total_enrolled);
      setText('vol-dash-completed', stats.total_attended);
      setText('vol-dash-certs', stats.total_certificates);
      setText('vol-dash-hours', (stats.total_hours || 0) + 'h');
      setText('vol-dash-badges', stats.total_certificates > 0 ? (stats.total_certificates + 2) : 1);
    }

    // Load enrollments list
    const { ok: enrOk, data: enrData } = await api.request('/api/volunteers/me/enrollments');
    const enrollmentsList = document.getElementById('vol-enrollments-list');
    const countBadge = document.getElementById('vol-enrollment-count');

    if (enrOk && enrData.enrollments) {
      if (countBadge) countBadge.textContent = `${enrData.enrollments.length} Events`;
      const upcoming = enrData.enrollments.filter(e => e.event && new Date(e.event.event_date) >= new Date().setHours(0,0,0,0));
      setText('vol-dash-upcoming', upcoming.length);

      if (enrData.enrollments.length === 0) {
        if (enrollmentsList) {
          enrollmentsList.innerHTML = `
            <div style="padding: 18px; color: var(--text-secondary); text-align: center;">
              You have not enrolled in any events yet. Explore upcoming causes above to get involved!
            </div>
          `;
        }
      } else if (enrollmentsList) {
        enrollmentsList.innerHTML = enrData.enrollments.map(e => `
          <div class="dash-enrollment-item">
            <div>
              <strong style="color: var(--text-primary); font-size: 0.95rem;">${e.event?.title || 'Event'}</strong>
              <div style="font-size: 0.8rem; color: var(--text-secondary);">
                <i class="fa-solid fa-location-dot"></i> ${e.event?.city || 'India'} &nbsp;·&nbsp;
                <i class="fa-solid fa-calendar"></i> ${formatDate(e.event?.event_date)}
              </div>
            </div>
            <div style="display:flex; align-items:center; gap: 10px;">
              ${e.attended ? '<span class="nav-role-badge"><i class="fa-solid fa-circle-check"></i> Attended</span>' : '<span style="font-size: 0.75rem; color: var(--secondary);">Registered</span>'}
              ${e.certificate_issued ? '<span class="type-badge badge-vol"><i class="fa-solid fa-certificate"></i> Verified Certificate</span>' : ''}
              ${!e.attended ? `<button class="btn btn-ghost btn-sm unenroll-btn" data-event-id="${e.event_id}" style="padding: 6px 12px; font-size: 0.75rem;">Cancel</button>` : ''}
            </div>
          </div>
        `).join('');

        enrollmentsList.querySelectorAll('.unenroll-btn').forEach(btn => {
          btn.addEventListener('click', async () => {
            const eventId = btn.getAttribute('data-event-id');
            if (confirm('Cancel your enrollment for this event?')) {
              await unenrollFromEvent(eventId);
            }
          });
        });
      }
    }

    // Load Smart Matches
    const { ok: matchOk, data: matchData } = await api.request('/api/volunteers/me/matches');
    const matchesList = document.getElementById('vol-matches-list');
    if (matchOk && matchData.matches && matchesList) {
      if (matchData.matches.length === 0) {
        matchesList.innerHTML = '<div style="color: var(--text-secondary);">No new upcoming matches at this time. Check back soon!</div>';
      } else {
        matchesList.innerHTML = matchData.matches.slice(0, 3).map(evt => `
          <div class="glass-card event-card" style="padding: 16px;">
            <span class="event-category">${evt.category}</span>
            <h4 style="margin: 8px 0; color: #fff;">${evt.title}</h4>
            <p style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 12px;">
              <i class="fa-solid fa-location-dot"></i> ${evt.city} &nbsp;·&nbsp; <i class="fa-solid fa-calendar"></i> ${formatDate(evt.event_date)}
            </p>
            <button type="button" class="btn btn-primary btn-sm enroll-btn" data-event-id="${evt.id}">Enroll in Match</button>
          </div>
        `).join('');

        matchesList.querySelectorAll('.enroll-btn').forEach(b => {
          b.addEventListener('click', () => enrollInEvent(b.getAttribute('data-event-id')));
        });
      }
    }
  } else {
    if (authPrompt) authPrompt.style.display = 'block';
    if (extraSection) extraSection.style.display = 'none';
  }
}

async function hydrateNGODashboard() {
  const authPrompt = document.getElementById('ngo-auth-prompt');
  const extraSection = document.getElementById('ngo-dash-extra');

  if (currentRole === 'ngo' && currentUser) {
    if (authPrompt) authPrompt.style.display = 'none';
    if (extraSection) extraSection.style.display = 'block';

    const { ok, data: stats } = await api.request('/api/ngos/me/stats');
    if (ok) {
      setText('ngo-dash-vols', (stats.total_volunteers_enrolled || 0).toLocaleString());
      setText('ngo-dash-upcoming', stats.active_events || 0);
      setText('ngo-dash-events', stats.total_events || 0);
      setText('ngo-dash-attendance', stats.total_volunteers_enrolled > 0 
        ? Math.round((stats.total_volunteers_attended / stats.total_volunteers_enrolled) * 100) + '%' 
        : '100%');
      setText('ngo-dash-rating', stats.average_rating || '5.0');
      setText('ngo-dash-certs', (stats.total_volunteers_attended || 0).toLocaleString());
    }

    hydrateNGOEvents();
  } else {
    if (authPrompt) authPrompt.style.display = 'block';
    if (extraSection) extraSection.style.display = 'none';
  }
}

async function hydrateNGOEvents() {
  const eventsList = document.getElementById('ngo-events-list');
  if (!eventsList) return;

  const { ok, data } = await api.request('/api/ngos/me/events');
  if (ok && data.events) {
    if (data.events.length === 0) {
      eventsList.innerHTML = `
        <div style="padding: 24px; text-align: center; color: var(--text-secondary);">
          No events created yet. Click "Post New Event" to publish your first volunteer opportunity!
        </div>
      `;
    } else {
      eventsList.innerHTML = data.events.map(evt => `
        <div class="dash-enrollment-item">
          <div>
            <strong style="color: var(--text-primary); font-size: 0.95rem;">${evt.title}</strong>
            <div style="font-size: 0.8rem; color: var(--text-secondary);">
              <i class="fa-solid fa-location-dot"></i> ${evt.city || 'India'} &nbsp;·&nbsp;
              <i class="fa-solid fa-calendar"></i> ${formatDate(evt.event_date)} &nbsp;·&nbsp;
              <span class="type-badge badge-ngo">${evt.category}</span>
            </div>
          </div>
          <div style="display: flex; gap: 8px;">
            <button type="button" class="btn btn-outline btn-sm view-roster-btn" data-event-id="${evt.id}" data-event-title="${evt.title}">
              <i class="fa-solid fa-users"></i> Roster (${evt.enrolled_count || 0})
            </button>
            ${evt.status === 'active' ? `<button type="button" class="btn btn-ghost btn-sm cancel-evt-btn" data-event-id="${evt.id}" style="color: #ef5350;">Cancel</button>` : '<span style="font-size:0.8rem;color:var(--text-muted);align-self:center;">Cancelled</span>'}
          </div>
        </div>
      `).join('');

      // Attach Roster Modal listeners
      eventsList.querySelectorAll('.view-roster-btn').forEach(b => {
        b.addEventListener('click', () => {
          const eventId = b.getAttribute('data-event-id');
          const eventTitle = b.getAttribute('data-event-title');
          openRosterModal(eventId, eventTitle);
        });
      });

      // Attach Cancel Event listener
      eventsList.querySelectorAll('.cancel-evt-btn').forEach(b => {
        b.addEventListener('click', async () => {
          if (confirm('Cancel this event?')) {
            const eventId = b.getAttribute('data-event-id');
            const { ok } = await api.request(`/api/events/${eventId}`, { method: 'DELETE' });
            if (ok) {
              alert('Event cancelled.');
              hydrateNGOEvents();
              loadUpcomingEvents();
            }
          }
        });
      });
    }
  }
}

// ------------------------------------------------------------
// Volunteer Attendance / Roster Management (NGO)
// ------------------------------------------------------------
async function openRosterModal(eventId, eventTitle) {
  const modal = document.getElementById('attendanceModal');
  const titleEl = document.getElementById('attendanceModalTitle');
  const listEl = document.getElementById('attendanceVolunteersList');

  if (titleEl) titleEl.textContent = `Volunteer Roster: ${eventTitle}`;
  if (listEl) listEl.innerHTML = '<div style="text-align:center; padding: 20px;"><i class="fa-solid fa-spinner fa-spin"></i> Loading roster...</div>';

  modal?.classList.add('active');

  const { ok, data } = await api.request(`/api/events/${eventId}/enrollments`);
  if (ok && data.enrollments) {
    if (data.enrollments.length === 0) {
      listEl.innerHTML = '<div style="padding: 24px; text-align: center; color: var(--text-secondary);">No volunteers have enrolled in this event yet.</div>';
    } else {
      listEl.innerHTML = data.enrollments.map(enr => `
        <div class="dash-enrollment-item">
          <div>
            <strong style="color: var(--text-primary); font-size: 0.95rem;">${enr.volunteer_name}</strong>
            <div style="font-size: 0.8rem; color: var(--text-secondary);">
              <i class="fa-solid fa-envelope"></i> ${enr.volunteer_email} &nbsp;·&nbsp;
              <i class="fa-solid fa-phone"></i> ${enr.volunteer_phone || 'N/A'}
            </div>
          </div>
          <div style="display: flex; align-items: center; gap: 8px;">
            ${enr.attended 
              ? '<span class="type-badge badge-vol"><i class="fa-solid fa-check-double"></i> Attended (' + enr.hours_logged + 'h)</span>'
              : `<button type="button" class="btn btn-primary btn-sm mark-att-btn" data-event-id="${eventId}" data-enrollment-id="${enr.id}"><i class="fa-solid fa-check"></i> Mark Attended</button>`
            }
          </div>
        </div>
      `).join('');

      listEl.querySelectorAll('.mark-att-btn').forEach(b => {
        b.addEventListener('click', async () => {
          const enrId = b.getAttribute('data-enrollment-id');
          const hours = prompt('Enter volunteer hours completed:', '4.0');
          if (hours !== null) {
            const { ok } = await api.request(`/api/events/${eventId}/attendance`, {
              method: 'POST',
              body: JSON.stringify({
                enrollment_id: parseInt(enrId),
                attended: true,
                hours_logged: parseFloat(hours || '4.0'),
                certificate_issued: true
              })
            });
            if (ok) {
              alert('✅ Attendance recorded and certificate issued!');
              openRosterModal(eventId, eventTitle);
              hydrateNGODashboard();
            }
          }
        });
      });
    }
  }
}

// ------------------------------------------------------------
// Utility Helpers
// ------------------------------------------------------------
function setText(id, text) {
  const el = document.getElementById(id);
  if (el) el.textContent = text !== undefined && text !== null ? text : '-';
}

function getCategoryEmoji(category) {
  if (!category) return '🤝';
  const cat = category.toLowerCase();
  if (cat.includes('tree') || cat.includes('environment')) return '🌳';
  if (cat.includes('blood')) return '🩸';
  if (cat.includes('edu')) return '📚';
  if (cat.includes('food')) return '🍱';
  if (cat.includes('animal')) return '🐾';
  if (cat.includes('women')) return '👩';
  if (cat.includes('health') || cat.includes('medical')) return '🏥';
  return '🤝';
}

function formatDate(dateStr) {
  if (!dateStr) return 'Upcoming';
  const d = new Date(dateStr);
  return d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });
}
