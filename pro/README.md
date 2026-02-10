# HoneyBadger Pro - Shop Management System

A locally-hosted web application for managing jobs and tracking time in a machine shop.

## Features

### For Workers (Basic Users)
- **Job Board** - View all available jobs
- **Join Jobs** - Add yourself to jobs that aren't full
- **Clock In/Out** - Track time on multiple jobs simultaneously
- **My Jobs** - See jobs you're assigned to
- **Mark Complete** - Submit finished jobs for review

### For Bosses (Admin Users)
- **Add Jobs** - Create new jobs with name, description, requirements, max workers
- **Auto-Review Option** - Jobs can auto-complete or require manual approval
- **Assign Workers** - Force-assign users to jobs
- **Review Queue** - Approve or reopen submitted jobs
- **User Management** - Create and delete user accounts
- **Archive** - View completed jobs with total time and workers

## Quick Start (Windows - No Docker)

### Prerequisites
1. **Python 3.11+** - [Download](https://www.python.org/downloads/)
2. **PostgreSQL** - [Download](https://www.postgresql.org/download/windows/)

### Setup

1. **Install PostgreSQL** and create the database:
   ```sql
   -- Open pgAdmin or psql and run:
   CREATE DATABASE honeybadger;
   CREATE USER honeybadger WITH PASSWORD 'honeybadger';
   GRANT ALL PRIVILEGES ON DATABASE honeybadger TO honeybadger;
   ```

2. **Run setup script:**
   ```
   Double-click: pro\setup_windows.bat
   ```

3. **Start the server:**
   ```
   Double-click: pro\run_server.bat
   ```

4. **Open in browser:**
   ```
   http://localhost:8000
   ```

5. **First user becomes Admin!** Create your boss account first.

## Quick Start (Docker - Recommended)

If you have Docker installed, this is the easiest way:

```bash
cd pro
docker-compose up -d
```

Then open: `http://localhost:8000`

## Network Access

To access from phones/other computers on your shop WiFi:

1. Find your computer's IP address:
   ```
   ipconfig
   ```
   Look for `IPv4 Address` (e.g., `192.168.1.50`)

2. Everyone connects to:
   ```
   http://192.168.1.50:8000
   ```

3. **Tip:** Set a static IP on the server computer so the address doesn't change.

## Data Model

| Table | Purpose |
|-------|---------|
| `users` | Worker accounts with roles (admin/basic) |
| `jobs` | Work orders with requirements and settings |
| `job_assignments` | Links workers to jobs |
| `time_entries` | Clock in/out records |

## API Documentation

Once running, visit `http://localhost:8000/docs` for interactive API docs.

## Configuration

Edit `pro/backend/config.py`:

```python
# Database connection
DATABASE_URL = "postgresql://user:password@localhost:5432/honeybadger"

# JWT secret (change in production!)
SECRET_KEY = "your-secret-key-here"
```

## Troubleshooting

### "Database connection failed"
- Make sure PostgreSQL is running
- Check DATABASE_URL in config.py
- Verify database and user were created

### "Can't connect from phone"
- Server and phone must be on same WiFi
- Check Windows Firewall allows port 8000
- Use computer's IP, not `localhost`

### "First user isn't admin"
- Database might have old data
- Reset with: `DROP DATABASE honeybadger; CREATE DATABASE honeybadger;`

## Tech Stack

- **Backend:** FastAPI (Python)
- **Database:** PostgreSQL
- **Frontend:** HTML/CSS/JavaScript (no framework)
- **Auth:** JWT tokens
