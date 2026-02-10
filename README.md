# HoneyBadger Tool

A cross-platform utility app for CNC machinists, featuring calculators and time tracking tools.

**Developed by TripactEntertainment**

## Versions

| Version | Description | Platform |
|---------|-------------|----------|
| **HoneyBadger** | Personal offline tool | Windows, Android |
| **HoneyBadger Pro** | Shop management system | Web (any device) |

---

## HoneyBadger (Personal Version)

### Features

### 🔧 Key Crest Calculator
Calculate key crest dimensions for precision machining work.

### 📏 Point to Point Calculator
Calculate distances between coordinate points - essential for CNC programming.

### ⏱️ Task Tracker
- Track time spent on jobs with punch in/out functionality
- Multiple time entries per task
- Priority levels (Low, Normal, High, Urgent)
- Archive completed tasks
- View total time worked per task

### Installation

#### Windows
1. Download or clone the repository
2. Run `HoneyBadger.pyw` or `install_and_run.bat`

#### Android
1. **[Download the APK (v1.3)](https://www.dropbox.com/scl/fi/2fc2kyai2gfos738t2sgy/honeybadger-1.3-arm64-v8a-debug.apk?rlkey=q0bjasbf7hsllazaqqve4jhk3&st=d5pd9h4k&dl=0)**
2. Install on your Android device (enable "Install from unknown sources")

---

## HoneyBadger Pro (Shop Management)

A locally-hosted web app for managing jobs and workers across the whole shop.

### Features

- **Job Board** - Central view of all shop jobs
- **Multi-user** - Admin and Worker roles
- **Time Tracking** - Clock in/out on multiple jobs
- **Job Assignment** - Workers can join jobs, bosses can assign
- **Review System** - Jobs can auto-complete or require approval
- **Works on ANY device** - iPhone, Android, Desktop via browser

### Quick Start

See [pro/README.md](pro/README.md) for full setup instructions.

```bash
# With Docker:
cd pro
docker-compose up -d
# Open http://localhost:8000
```

---

## Project Structure

```
HoneyBadgerTool/
├── calculators/          # Core calculation logic
├── ui_tkinter/           # Windows desktop UI
├── ui_kivy/              # Android mobile UI
├── pro/                  # HoneyBadger Pro (web app)
│   ├── backend/          # FastAPI server
│   ├── frontend/         # Web interface
│   └── docker-compose.yml
├── Apptools/             # Icons and assets
├── main.py               # Platform-detecting launcher
└── buildozer.spec        # Android build configuration
```

## License

Proprietary - © TripactEntertainment

## Version

- HoneyBadger: **1.3**
- HoneyBadger Pro: **1.0**
