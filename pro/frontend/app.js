/**
 * HoneyBadger Pro - Frontend Application
 */

const API_URL = window.location.origin;

// State
let currentUser = null;
let authToken = null;
let jobs = [];
let myJobs = [];
let archivedJobs = [];
let users = [];
let activeClocks = [];
let clockTimers = {};

// ==================== AUTH ====================

async function login(username, password) {
    try {
        const response = await fetch(`${API_URL}/api/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Login failed');
        }
        
        const data = await response.json();
        authToken = data.access_token;
        currentUser = data.user;
        localStorage.setItem('token', authToken);
        localStorage.setItem('user', JSON.stringify(currentUser));
        
        showMainApp();
    } catch (error) {
        document.getElementById('login-error').textContent = error.message;
    }
}

async function register(username, initials, password) {
    try {
        const response = await fetch(`${API_URL}/api/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, initials, password })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Registration failed');
        }
        
        // Auto-login after registration
        await login(username, password);
    } catch (error) {
        document.getElementById('register-error').textContent = error.message;
    }
}

function logout() {
    authToken = null;
    currentUser = null;
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    clearAllTimers();
    showLoginScreen();
}

function getAuthHeaders() {
    return {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json'
    };
}

// ==================== API CALLS ====================

async function fetchJobs() {
    try {
        const response = await fetch(`${API_URL}/api/jobs`, {
            headers: getAuthHeaders()
        });
        if (response.ok) {
            jobs = await response.json();
            renderJobBoard();
            renderMyJobs();
        }
    } catch (error) {
        console.error('Error fetching jobs:', error);
    }
}

async function fetchArchivedJobs() {
    try {
        const response = await fetch(`${API_URL}/api/jobs/archived`, {
            headers: getAuthHeaders()
        });
        if (response.ok) {
            archivedJobs = await response.json();
            renderArchive();
        }
    } catch (error) {
        console.error('Error fetching archived jobs:', error);
    }
}

async function fetchActiveClocks() {
    try {
        const response = await fetch(`${API_URL}/api/time/active`, {
            headers: getAuthHeaders()
        });
        if (response.ok) {
            activeClocks = await response.json();
            renderActiveClocks();
        }
    } catch (error) {
        console.error('Error fetching active clocks:', error);
    }
}

async function fetchUsers() {
    if (currentUser.role !== 'admin') return;
    try {
        const response = await fetch(`${API_URL}/api/users`, {
            headers: getAuthHeaders()
        });
        if (response.ok) {
            users = await response.json();
            renderUsers();
        }
    } catch (error) {
        console.error('Error fetching users:', error);
    }
}

async function createJob(jobData) {
    try {
        const response = await fetch(`${API_URL}/api/jobs`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify(jobData)
        });
        if (response.ok) {
            fetchJobs();
            document.getElementById('add-job-form').reset();
        } else {
            const error = await response.json();
            alert(error.detail || 'Failed to create job');
        }
    } catch (error) {
        console.error('Error creating job:', error);
    }
}

async function joinJob(jobId) {
    try {
        const response = await fetch(`${API_URL}/api/jobs/${jobId}/join`, {
            method: 'POST',
            headers: getAuthHeaders()
        });
        if (response.ok) {
            fetchJobs();
            closeModal();
        } else {
            const error = await response.json();
            alert(error.detail || 'Failed to join job');
        }
    } catch (error) {
        console.error('Error joining job:', error);
    }
}

async function leaveJob(jobId) {
    try {
        const response = await fetch(`${API_URL}/api/jobs/${jobId}/leave`, {
            method: 'DELETE',
            headers: getAuthHeaders()
        });
        if (response.ok) {
            fetchJobs();
            closeModal();
        } else {
            const error = await response.json();
            alert(error.detail || 'Failed to leave job');
        }
    } catch (error) {
        console.error('Error leaving job:', error);
    }
}

async function clockIn(jobId) {
    try {
        const response = await fetch(`${API_URL}/api/time/clockin`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({ job_id: jobId })
        });
        if (response.ok) {
            fetchJobs();
            fetchActiveClocks();
            closeModal();
        } else {
            const error = await response.json();
            alert(error.detail || 'Failed to clock in');
        }
    } catch (error) {
        console.error('Error clocking in:', error);
    }
}

async function clockOut(jobId) {
    try {
        const response = await fetch(`${API_URL}/api/time/clockout`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({ job_id: jobId })
        });
        if (response.ok) {
            fetchJobs();
            fetchActiveClocks();
            closeModal();
        } else {
            const error = await response.json();
            alert(error.detail || 'Failed to clock out');
        }
    } catch (error) {
        console.error('Error clocking out:', error);
    }
}

async function markJobComplete(jobId) {
    if (!confirm('Mark this job as complete?')) return;
    try {
        const response = await fetch(`${API_URL}/api/jobs/${jobId}/mark-complete`, {
            method: 'POST',
            headers: getAuthHeaders()
        });
        if (response.ok) {
            fetchJobs();
            fetchActiveClocks();
            closeModal();
        } else {
            const error = await response.json();
            alert(error.detail || 'Failed to mark job complete');
        }
    } catch (error) {
        console.error('Error marking job complete:', error);
    }
}

async function approveJob(jobId) {
    try {
        const response = await fetch(`${API_URL}/api/jobs/${jobId}/approve`, {
            method: 'POST',
            headers: getAuthHeaders()
        });
        if (response.ok) {
            fetchJobs();
            fetchArchivedJobs();
        } else {
            const error = await response.json();
            alert(error.detail || 'Failed to approve job');
        }
    } catch (error) {
        console.error('Error approving job:', error);
    }
}

async function reopenJob(jobId) {
    try {
        const response = await fetch(`${API_URL}/api/jobs/${jobId}/reopen`, {
            method: 'POST',
            headers: getAuthHeaders()
        });
        if (response.ok) {
            fetchJobs();
        } else {
            const error = await response.json();
            alert(error.detail || 'Failed to reopen job');
        }
    } catch (error) {
        console.error('Error reopening job:', error);
    }
}

async function deleteJob(jobId) {
    if (!confirm('Delete this job permanently?')) return;
    try {
        const response = await fetch(`${API_URL}/api/jobs/${jobId}`, {
            method: 'DELETE',
            headers: getAuthHeaders()
        });
        if (response.ok) {
            fetchJobs();
            closeModal();
        } else {
            const error = await response.json();
            alert(error.detail || 'Failed to delete job');
        }
    } catch (error) {
        console.error('Error deleting job:', error);
    }
}

// ==================== RENDERING ====================

function renderJobBoard() {
    const container = document.getElementById('jobs-list');
    const activeJobs = jobs.filter(j => !j.is_archived && !j.marked_for_review);
    
    if (activeJobs.length === 0) {
        container.innerHTML = '<div class="empty-state"><p>No jobs available</p></div>';
        return;
    }
    
    container.innerHTML = activeJobs.map(job => {
        const hasActiveWorker = job.assignments.some(a => a.is_clocked_in);
        const statusClass = hasActiveWorker ? 'in-progress' : '';
        const statusBadge = hasActiveWorker ? 
            '<span class="status-badge in-progress">In Progress</span>' :
            '<span class="status-badge open">Open</span>';
        
        return `
            <div class="job-card ${statusClass}" onclick="openJobModal(${job.id})">
                <h3>
                    ${escapeHtml(job.job_name)}
                    ${statusBadge}
                </h3>
                ${job.description ? `<p class="description">${escapeHtml(job.description)}</p>` : ''}
                <div class="job-meta">
                    <span>Workers: ${job.current_workers}/${job.max_workers}</span>
                    <span>Time: ${formatDuration(job.total_time_seconds)}</span>
                </div>
            </div>
        `;
    }).join('');
    
    // Render review queue for admin
    if (currentUser.role === 'admin') {
        renderReviewQueue();
    }
}

function renderReviewQueue() {
    const container = document.getElementById('review-queue');
    const reviewJobs = jobs.filter(j => j.marked_for_review);
    
    if (reviewJobs.length === 0) {
        container.innerHTML = '<p class="empty-state">No jobs pending review</p>';
        return;
    }
    
    container.innerHTML = reviewJobs.map(job => `
        <div class="job-card review">
            <h3>
                ${escapeHtml(job.job_name)}
                <span class="status-badge review">Pending Review</span>
            </h3>
            <div class="job-meta">
                <span>Workers: ${job.current_workers}</span>
                <span>Time: ${formatDuration(job.total_time_seconds)}</span>
            </div>
            <div style="margin-top: 10px;">
                <button class="btn btn-small btn-primary" onclick="event.stopPropagation(); approveJob(${job.id})">Approve</button>
                <button class="btn btn-small btn-secondary" onclick="event.stopPropagation(); reopenJob(${job.id})">Reopen</button>
            </div>
        </div>
    `).join('');
}

function renderMyJobs() {
    const container = document.getElementById('my-jobs-list');
    myJobs = jobs.filter(j => 
        !j.is_archived && 
        j.assignments.some(a => a.user_id === currentUser.id)
    );
    
    if (myJobs.length === 0) {
        container.innerHTML = '<div class="empty-state"><p>You\'re not assigned to any jobs</p><p>Join a job from the Job Board!</p></div>';
        return;
    }
    
    container.innerHTML = myJobs.map(job => {
        const myAssignment = job.assignments.find(a => a.user_id === currentUser.id);
        const isClockedIn = myAssignment?.is_clocked_in;
        
        return `
            <div class="job-card ${isClockedIn ? 'in-progress' : ''}" onclick="openJobModal(${job.id})">
                <h3>
                    ${escapeHtml(job.job_name)}
                    ${isClockedIn ? '<span class="status-badge in-progress">Clocked In</span>' : ''}
                </h3>
                <div class="job-meta">
                    <span>Time: ${formatDuration(job.total_time_seconds)}</span>
                </div>
            </div>
        `;
    }).join('');
}

function renderActiveClocks() {
    const container = document.getElementById('active-clocks');
    clearAllTimers();
    
    if (activeClocks.length === 0) {
        container.innerHTML = '';
        return;
    }
    
    container.innerHTML = `
        <h3>⏱️ Currently Clocked In</h3>
        ${activeClocks.map(clock => {
            const timerId = `clock-${clock.job_id}`;
            return `
                <div class="active-clock-item">
                    <div>
                        <strong>${escapeHtml(clock.job_name)}</strong>
                    </div>
                    <div>
                        <span class="clock-duration" id="${timerId}">--:--:--</span>
                        <button class="btn btn-small btn-danger" onclick="clockOut(${clock.job_id})">Clock Out</button>
                    </div>
                </div>
            `;
        }).join('')}
    `;
    
    // Start timers
    activeClocks.forEach(clock => {
        startClockTimer(clock.job_id, new Date(clock.clock_in));
    });
}

function renderArchive() {
    const container = document.getElementById('archive-list');
    
    if (archivedJobs.length === 0) {
        container.innerHTML = '<div class="empty-state"><p>No completed jobs yet</p></div>';
        return;
    }
    
    container.innerHTML = archivedJobs.map(job => `
        <div class="job-card" onclick="openJobModal(${job.id}, true)">
            <h3>
                ${escapeHtml(job.job_name)}
                <span class="status-badge complete">Complete</span>
            </h3>
            <div class="job-meta">
                <span>Workers: ${job.current_workers}</span>
                <span>Total Time: ${formatDuration(job.total_time_seconds)}</span>
                <span>Completed: ${formatDate(job.completed_at)}</span>
            </div>
        </div>
    `).join('');
}

function renderUsers() {
    const container = document.getElementById('users-list');
    
    container.innerHTML = users.map(user => `
        <div class="user-card">
            <div>
                <span class="user-name">${escapeHtml(user.username)} (${user.initials})</span>
                <span class="user-role ${user.role}">${user.role}</span>
            </div>
            ${user.id !== currentUser.id ? `
                <button class="btn btn-small btn-danger" onclick="deleteUser(${user.id})">Delete</button>
            ` : ''}
        </div>
    `).join('');
}

// ==================== MODAL ====================

function openJobModal(jobId, isArchived = false) {
    const job = isArchived ? 
        archivedJobs.find(j => j.id === jobId) : 
        jobs.find(j => j.id === jobId);
    
    if (!job) return;
    
    document.getElementById('modal-job-name').textContent = job.job_name;
    document.getElementById('modal-job-description').textContent = job.description || 'No description';
    
    const reqContainer = document.getElementById('modal-requirements');
    if (job.requirements) {
        reqContainer.innerHTML = `<h4>Requirements</h4><p>${escapeHtml(job.requirements)}</p>`;
        reqContainer.style.display = 'block';
    } else {
        reqContainer.style.display = 'none';
    }
    
    document.getElementById('modal-workers').textContent = `${job.current_workers}/${job.max_workers}`;
    
    let status = 'Open';
    if (job.is_complete) status = 'Complete';
    else if (job.marked_for_review) status = 'Pending Review';
    else if (job.assignments.some(a => a.is_clocked_in)) status = 'In Progress';
    document.getElementById('modal-status').textContent = status;
    
    document.getElementById('modal-time').textContent = formatDuration(job.total_time_seconds);
    
    // Assignments
    const assignContainer = document.getElementById('modal-assignments');
    if (job.assignments.length === 0) {
        assignContainer.innerHTML = '<p>No workers assigned</p>';
    } else {
        assignContainer.innerHTML = job.assignments.map(a => `
            <div class="assignment-item">
                <span class="initials">${a.initials}</span>
                <span>${escapeHtml(a.username)}</span>
                ${a.is_clocked_in ? '<span class="clocked-in">● Clocked In</span>' : ''}
            </div>
        `).join('');
    }
    
    // Actions
    const actionsContainer = document.getElementById('modal-actions');
    const isAssigned = job.assignments.some(a => a.user_id === currentUser.id);
    const isClockedIn = job.assignments.find(a => a.user_id === currentUser.id)?.is_clocked_in;
    const isFull = job.current_workers >= job.max_workers;
    const isAdmin = currentUser.role === 'admin';
    
    let actions = [];
    
    if (!job.is_archived && !job.marked_for_review) {
        if (!isAssigned && !isFull) {
            actions.push(`<button class="btn btn-primary" onclick="joinJob(${job.id})">Join Job</button>`);
        }
        
        if (isAssigned) {
            if (isClockedIn) {
                actions.push(`<button class="btn btn-warning" onclick="clockOut(${job.id})">Clock Out</button>`);
            } else {
                actions.push(`<button class="btn btn-primary" onclick="clockIn(${job.id})">Clock In</button>`);
                actions.push(`<button class="btn btn-secondary" onclick="leaveJob(${job.id})">Leave Job</button>`);
            }
            actions.push(`<button class="btn" onclick="markJobComplete(${job.id})">Mark Complete</button>`);
        }
        
        if (isAdmin) {
            actions.push(`<button class="btn btn-danger" onclick="deleteJob(${job.id})">Delete Job</button>`);
        }
    }
    
    actionsContainer.innerHTML = actions.join('');
    
    document.getElementById('job-modal').classList.add('active');
}

function closeModal() {
    document.getElementById('job-modal').classList.remove('active');
}

// ==================== UTILITIES ====================

function formatDuration(seconds) {
    if (!seconds || seconds < 0) return '0:00:00';
    const hrs = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    return `${hrs}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

function formatDate(dateStr) {
    if (!dateStr) return 'N/A';
    return new Date(dateStr).toLocaleDateString();
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function startClockTimer(jobId, startTime) {
    const timerId = `clock-${jobId}`;
    const element = document.getElementById(timerId);
    if (!element) return;
    
    function update() {
        const now = new Date();
        const diff = (now - startTime) / 1000;
        element.textContent = formatDuration(diff);
    }
    
    update();
    clockTimers[jobId] = setInterval(update, 1000);
}

function clearAllTimers() {
    Object.values(clockTimers).forEach(timer => clearInterval(timer));
    clockTimers = {};
}

// ==================== NAVIGATION ====================

function showLoginScreen() {
    document.getElementById('login-screen').classList.add('active');
    document.getElementById('register-screen').classList.remove('active');
    document.getElementById('main-app').classList.remove('active');
}

function showRegisterScreen() {
    document.getElementById('login-screen').classList.remove('active');
    document.getElementById('register-screen').classList.add('active');
}

function showMainApp() {
    document.getElementById('login-screen').classList.remove('active');
    document.getElementById('register-screen').classList.remove('active');
    document.getElementById('main-app').classList.add('active');
    
    // Set user display
    document.getElementById('user-display').textContent = 
        `${currentUser.initials} (${currentUser.role})`;
    
    // Show admin elements
    if (currentUser.role === 'admin') {
        document.body.classList.add('is-admin');
    } else {
        document.body.classList.remove('is-admin');
    }
    
    // Load data
    fetchJobs();
    fetchArchivedJobs();
    fetchActiveClocks();
    if (currentUser.role === 'admin') {
        fetchUsers();
    }
    
    // Start refresh interval
    setInterval(() => {
        fetchJobs();
        fetchActiveClocks();
    }, 30000); // Refresh every 30 seconds
}

function switchPage(pageName) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    
    document.getElementById(pageName).classList.add('active');
    document.querySelector(`[data-page="${pageName}"]`).classList.add('active');
    
    // Refresh data based on page
    if (pageName === 'archive') {
        fetchArchivedJobs();
    } else if (pageName === 'admin') {
        fetchUsers();
    }
}

// ==================== EVENT LISTENERS ====================

document.addEventListener('DOMContentLoaded', () => {
    // Check for existing session
    const savedToken = localStorage.getItem('token');
    const savedUser = localStorage.getItem('user');
    
    if (savedToken && savedUser) {
        authToken = savedToken;
        currentUser = JSON.parse(savedUser);
        showMainApp();
    } else {
        showLoginScreen();
    }
    
    // Login form
    document.getElementById('login-form').addEventListener('submit', (e) => {
        e.preventDefault();
        const username = document.getElementById('login-username').value;
        const password = document.getElementById('login-password').value;
        login(username, password);
    });
    
    // Register form
    document.getElementById('register-form').addEventListener('submit', (e) => {
        e.preventDefault();
        const username = document.getElementById('reg-username').value;
        const initials = document.getElementById('reg-initials').value;
        const password = document.getElementById('reg-password').value;
        register(username, initials, password);
    });
    
    // Show register/login toggles
    document.getElementById('show-register').addEventListener('click', showRegisterScreen);
    document.getElementById('show-login').addEventListener('click', showLoginScreen);
    
    // Logout
    document.getElementById('logout-btn').addEventListener('click', logout);
    
    // Navigation
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            switchPage(btn.dataset.page);
        });
    });
    
    // Add job form
    document.getElementById('add-job-form').addEventListener('submit', (e) => {
        e.preventDefault();
        createJob({
            job_name: document.getElementById('job-name').value,
            description: document.getElementById('job-description').value || null,
            requirements: document.getElementById('job-requirements').value || null,
            max_workers: parseInt(document.getElementById('job-max-workers').value) || 1,
            auto_review: document.getElementById('job-auto-review').checked
        });
    });
    
    // Modal close
    document.querySelector('.modal .close').addEventListener('click', closeModal);
    document.getElementById('job-modal').addEventListener('click', (e) => {
        if (e.target.id === 'job-modal') closeModal();
    });
});

// Delete user (admin)
async function deleteUser(userId) {
    if (!confirm('Delete this user?')) return;
    try {
        const response = await fetch(`${API_URL}/api/users/${userId}`, {
            method: 'DELETE',
            headers: getAuthHeaders()
        });
        if (response.ok) {
            fetchUsers();
        } else {
            const error = await response.json();
            alert(error.detail || 'Failed to delete user');
        }
    } catch (error) {
        console.error('Error deleting user:', error);
    }
}
