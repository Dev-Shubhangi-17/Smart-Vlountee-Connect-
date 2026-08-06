// Smart Volunteer Connect — Frontend API Integration
const API_BASE_URL = (window.location.origin.includes('localhost') || window.location.origin.includes('127.0.0.1')) 
  ? 'http://localhost:5000' 
  : '';

document.addEventListener('DOMContentLoaded', function() {

  // ============================================================
  // VOLUNTEER REGISTRATION FORM
  // ============================================================
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
      
      // Get selected interests
      const interestCheckboxes = document.querySelectorAll('#volunteerForm .interest-chip-wrap input[type="checkbox"]:checked');
      const interests = Array.from(interestCheckboxes).map(cb => cb.nextElementSibling.textContent.replace(/^[^\w]+/, '').trim());
      
      if (!name || !email || !phone || !city) {
        alert('⚠️ Please fill in all required fields (Name, Email, Phone, Location)');
        return;
      }
      
      const payload = {
        name,
        email,
        password: 'Password123!', // default temp password for public reg form
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
        
        const response = await fetch(`${API_BASE_URL}/api/volunteers`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        
        const data = await response.json();
        
        if (response.ok) {
          alert(`✅ Registration successful! Welcome ${data.volunteer.name}. Your profile ID is #${data.volunteer.id}`);
          volunteerForm.reset();
          loadLiveStats();
        } else {
          alert(`❌ Registration failed: ${data.error || data.detail || 'Unknown error'}`);
        }
      } catch (error) {
        console.error('API Error:', error);
        alert('❌ Could not connect to backend server. Make sure Flask is running on http://localhost:5000');
      } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
      }
    });
  }

  // ============================================================
  // NGO REGISTRATION FORM
  // ============================================================
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
      
      if (!name || !email || !phone || !city) {
        alert('⚠️ Please fill in all required fields');
        return;
      }
      
      const payload = {
        name,
        email,
        password: 'Password123!', // default temp password
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
        
        const response = await fetch(`${API_BASE_URL}/api/ngos`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        
        const data = await response.json();
        
        if (response.ok) {
          alert(`✅ NGO Registration successful! ${data.ngo.name} registered under ID #${data.ngo.id}`);
          ngoForm.reset();
          loadLiveStats();
        } else {
          alert(`❌ Registration failed: ${data.error || data.detail || 'Unknown error'}`);
        }
      } catch (error) {
        console.error('API Error:', error);
        alert('❌ Could not connect to backend server. Make sure Flask is running on http://localhost:5000');
      } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
      }
    });
  }

  // ============================================================
  // CONTACT FORM
  // ============================================================
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
        
        const response = await fetch(`${API_BASE_URL}/api/contact`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        
        const data = await response.json();
        
        if (response.ok) {
          alert(`✅ ${data.message || 'Message sent successfully!'}`);
          contactForm.reset();
        } else {
          alert(`❌ Error: ${data.error || 'Failed to send message'}`);
        }
      } catch (error) {
        console.error('API Error:', error);
        alert('❌ Could not connect to backend server.');
      } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
      }
    });
  }

  // Initial loads
  loadLiveStats();
  loadUpcomingEvents();
});

// ============================================================
// LOAD LIVE STATS
// ============================================================
async function loadLiveStats() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/stats`);
    if (!response.ok) return;
    const stats = await response.json();
    
    // Update hero stats if present
    const statNums = document.querySelectorAll('.hero-stat-num');
    if (statNums.length >= 3) {
      statNums[0].textContent = (stats.total_volunteers || 0) + '+';
      statNums[1].textContent = (stats.total_ngos || 0) + '+';
      statNums[2].textContent = (stats.total_events || 0) + '+';
    }
  } catch (err) {
    console.log('Live stats not available yet:', err);
  }
}

// ============================================================
// LOAD LIVE UPCOMING EVENTS
// ============================================================
async function loadUpcomingEvents() {
  const eventsGrid = document.querySelector('.events-grid');
  if (!eventsGrid) return;
  
  try {
    const response = await fetch(`${API_BASE_URL}/api/events`);
    if (!response.ok) return;
    const data = await response.json();
    
    if (data.events && data.events.length > 0) {
      eventsGrid.innerHTML = data.events.map((evt, idx) => `
        <div class="glass-card event-card anim anim-d${(idx % 3) + 1}">
          <div class="event-image">${getCategoryEmoji(evt.category)}</div>
          <div class="event-body">
            <span class="event-category">${evt.category || 'General'}</span>
            <h3>${evt.title}</h3>
            <div class="event-meta">
              <div class="event-meta-item"><i class="fa-solid fa-building-ngo"></i> ${evt.ngo?.name || 'Verified NGO'}</div>
              <div class="event-meta-item"><i class="fa-solid fa-location-dot"></i> ${evt.venue || evt.city || 'India'}</div>
              <div class="event-meta-item"><i class="fa-solid fa-calendar"></i> ${formatDate(evt.event_date)}</div>
            </div>
            <div class="event-footer">
              <div class="seats-badge">Seats: <span>${evt.spots_left !== null ? evt.spots_left + ' left' : 'Open'}</span></div>
              <a href="#volunteer-reg" class="btn btn-primary btn-sm">Register</a>
            </div>
          </div>
        </div>
      `).join('');
    }
  } catch (err) {
    console.log('Using default static events:', err);
  }
}

function getCategoryEmoji(category) {
  if (!category) return '🤝';
  cat = category.toLowerCase();
  if (cat.includes('tree') || cat.includes('environment')) return '🌳';
  if (cat.includes('blood')) return '🩸';
  if (cat.includes('edu')) return '📚';
  if (cat.includes('food')) return '🍱';
  if (cat.includes('animal')) return '🐾';
  return '🤝';
}

function formatDate(dateStr) {
  if (!dateStr) return 'Upcoming';
  const d = new Date(dateStr);
  return d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });
}
