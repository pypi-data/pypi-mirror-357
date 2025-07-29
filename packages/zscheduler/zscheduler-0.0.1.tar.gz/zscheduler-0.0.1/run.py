#!/usr/bin/env python3
"""
ZScheduler Application Launcher

This script provides a simple way to launch the ZScheduler application.
"""

import sys
import os

# Add the current directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import and run the application
from zscheduler_app.main import main

if __name__ == "__main__":
    main()
