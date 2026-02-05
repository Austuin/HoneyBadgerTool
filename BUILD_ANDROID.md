# Building the Android APK

## Google Colab Build (Recommended)

### Step 1: Open Colab
Go to https://colab.research.google.com and create a new notebook

### Step 2: Install Build Tools
Run this cell first:
```python
!pip install buildozer cython==0.29.33
!sudo apt-get update
!sudo apt-get install -y \
    python3-pip build-essential git python3 python3-dev \
    ffmpeg libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
    libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev zlib1g-dev \
    libgstreamer1.0 gstreamer1.0-plugins-base gstreamer1.0-plugins-good \
    libltdl-dev libffi-dev autoconf automake libtool libtool-bin
```

### Step 3: Upload Project Files
In Colab, click the **folder icon** on the left sidebar, then:
1. Create folder: `FunTools`
2. Inside `FunTools`, create folders: `calculators`, `ui_kivy`, `Apptools`
3. Upload these files:

**Root folder (FunTools/):**
- `main.py`
- `buildozer.spec`

**calculators/ folder:**
- `__init__.py`
- `key_crest.py`
- `point_to_point.py`
- `task_tracker.py`

**ui_kivy/ folder:**
- `__init__.py`
- `app.py`

**Apptools/ folder:**
- `Icon.png`
- `IconLoading.png`

### Step 4: Build the APK
```python
%cd /content/FunTools
!buildozer android debug
```

This takes 15-30 minutes the first time.

### Step 5: Download Your APK
When complete, find the APK at:
```
/content/FunTools/bin/honeybadger-1.1-debug.apk
```

Right-click → Download

---

## Quick Rebuild (After Changes)

If you've built before and just need to rebuild with changes:

```python
# Clean and rebuild
%cd /content/FunTools
!buildozer android clean
!buildozer android debug
```

---

## Installing on Android Phone

1. **Transfer APK** - Email it, use Google Drive, or USB cable
2. **Enable Unknown Sources** - Settings → Security → Install Unknown Apps
3. **Install** - Tap the APK file
4. **Find App** - Look for "HoneyBadger" in your app drawer

---

## Testing on Desktop First

Before building for Android, test the Kivy version locally:

```bash
# Install Kivy
pip install kivy

# Run the app
cd "E:\Fun Tools"
python ui_kivy/app.py
```

---

## Troubleshooting

**Build fails with "libtool not found":**
```python
!sudo apt-get install -y libtool libtool-bin
```

**Build fails with path errors:**
- Make sure your folder has NO SPACES in the name
- Use `FunTools` not `Fun Tools`

**APK won't install on phone:**
- Make sure "Install Unknown Apps" is enabled for your file manager
- Try enabling it for Google Drive/Chrome if transferring that way

---

## What's in Version 1.1

- Key Crest Calculator
- Point to Point Calculator  
- Task Tracker with:
  - Multiple punch in/out per task
  - Priority levels (Low, Normal, High, Urgent)
  - Auto-sorting by priority
  - Task archiving
  - Time tracking with totals
  - Save results to Downloads folder
