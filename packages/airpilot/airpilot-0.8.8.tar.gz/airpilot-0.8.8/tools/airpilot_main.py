#!/usr/bin/env python3
"""
AirPilot CLI entry point for Nuitka compilation
Uses absolute imports to avoid relative import issues
"""

import sys
import os
from pathlib import Path

# Add src to path for absolute imports
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Now we can import with absolute paths
from airpilot.cli import main

if __name__ == '__main__':
    main()