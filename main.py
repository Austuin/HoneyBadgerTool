"""
Honey Badger Tool Functions
Platform-aware launcher - runs tkinter on desktop, Kivy on Android
"""
import sys
import os

# Add the project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def detect_platform():
    """Detect whether we're running on Android or desktop"""
    try:
        # Kivy's platform detection
        from kivy.utils import platform
        return platform
    except ImportError:
        pass
    
    # Fallback detection
    if hasattr(sys, 'getandroidapilevel'):
        return 'android'
    
    # Check for common Android environment variables
    if 'ANDROID_ROOT' in os.environ or 'ANDROID_DATA' in os.environ:
        return 'android'
    
    # Default to desktop
    return 'desktop'


def run_tkinter():
    """Run the tkinter (desktop) version"""
    from ui_tkinter.app import run
    run()


def run_kivy():
    """Run the Kivy (Android) version"""
    from ui_kivy.app import run
    run()


def main():
    platform = detect_platform()
    print(f"Detected platform: {platform}")
    
    if platform == 'android':
        print("Starting Kivy (Android) interface...")
        run_kivy()
    else:
        # Desktop (Windows, Linux, macOS)
        print("Starting Tkinter (Desktop) interface...")
        run_tkinter()


if __name__ == '__main__':
    main()
