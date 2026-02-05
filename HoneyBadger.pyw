"""
HoneyBadger Launcher (No Console Window)
Double-click this or point your shortcut here
"""
import sys
import os

# Add the project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui_tkinter.app import run
run()
