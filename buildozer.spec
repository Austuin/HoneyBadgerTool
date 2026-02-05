[app]

# Title of your application
title = HoneyBadger

# Package name
package.name = honeybadger

# Package domain (needed for android/ios packaging)
package.domain = org.honeybadger

# Source code directory
source.dir = .

# Source files to include
source.include_exts = py,png,jpg,kv,atlas,json

# Application version
version = 1.3

# Application requirements - add pyjnius for Android API access
requirements = python3,kivy,pyjnius

# Supported orientation (portrait, landscape, all)
orientation = portrait

# Android permissions
android.permissions = WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# Android API to use for build (use 33 for better compatibility)
android.api = 33

# Minimum API your APK will support
android.minapi = 21

# Android NDK version (r25b works with current Colab)
android.ndk = 25b

# Accept SDK license automatically
android.accept_sdk_license = True

# Use older gradle plugin version that works in Colab
android.gradle_dependencies = 
android.enable_androidx = True
android.add_aars = 

# Build only for arm64 (faster build, works on most modern phones)
android.archs = arm64-v8a

# Full screen mode (0 = no, 1 = yes)
fullscreen = 0

# Android app theme
android.apptheme = @android:style/Theme.NoTitleBar

# Presplash color (black to match app theme)
android.presplash_color = #000000

# Presplash image (loading screen)
presplash.filename = Apptools/IconLoading.png

# Icon
icon.filename = Apptools/Icon.png

# Entry point
# p4a.entrypoint = org.kivy.android.PythonActivity

# Bootstrap
p4a.bootstrap = sdl2

# Include patterns - make sure to include __init__.py files!
source.include_patterns = calculators/*.py, calculators/__init__.py, ui_kivy/*.py, ui_kivy/__init__.py, main.py, *.py

# Exclude desktop-only files
source.exclude_patterns = ui_tkinter/*,HoneyBadger.pyw,install_and_run.bat

# Main script
# android.entrypoint = main.py

[buildozer]

# Buildozer log level (0 = error only, 1 = info, 2 = debug)
log_level = 2

# Display warning if buildozer is outdated
warn_on_root = 1


