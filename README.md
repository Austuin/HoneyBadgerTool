# HoneyBadger Tool

A cross-platform utility app for CNC machinists, featuring calculators and time tracking tools.

**Developed by Tripact**

## Features

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

## Platforms

- **Windows** - Desktop application using Tkinter
- **Android** - Mobile app using Kivy

## Installation

### Windows
1. Download or clone the repository
2. Run `HoneyBadger.pyw` or `install_and_run.bat`

### Android
1. Download the APK from the releases
2. Install on your Android device (enable "Install from unknown sources")

## Building Android APK

See [BUILD_ANDROID.md](BUILD_ANDROID.md) for instructions on building the Android APK using Google Colab.

## Requirements

- Python 3.11+
- Tkinter (included with Python on Windows)
- Kivy (for Android builds)

## Project Structure

```
HoneyBadgerTool/
├── calculators/          # Core calculation logic
│   ├── key_crest.py
│   ├── point_to_point.py
│   └── task_tracker.py
├── ui_tkinter/           # Windows desktop UI
│   └── app.py
├── ui_kivy/              # Android mobile UI
│   └── app.py
├── Apptools/             # Icons and assets
├── main.py               # Platform-detecting launcher
├── HoneyBadger.pyw       # Windows launcher (no console)
└── buildozer.spec        # Android build configuration
```

## License

Proprietary - © Tripact

## Version

Current: **1.3**
