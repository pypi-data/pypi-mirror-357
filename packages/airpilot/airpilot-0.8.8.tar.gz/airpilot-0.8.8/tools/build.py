#!/usr/bin/env python3
"""
Simple Nuitka build for AirPilot
"""
import subprocess
import platform
import shutil
from pathlib import Path

# Clean all build artifacts
build_dirs = ["build", "dist", "*.build", "*.dist", "*.onefile-build"]
for pattern in build_dirs:
    for p in Path(".").glob(pattern):
        if p.exists():
            shutil.rmtree(p) if p.is_dir() else p.unlink()

# Create single dist directory
dist_dir = Path("dist")
dist_dir.mkdir(exist_ok=True)

# Binary name
binary_name = "airpilot.exe" if platform.system() == "Windows" else "airpilot"

# Build with Nuitka - everything goes to dist/
cmd = [
    "uv", "run", "nuitka",
    "--standalone", "--onefile",
    f"--output-dir=dist",
    f"--output-filename={binary_name}",
    "airpilot_main.py"
]

subprocess.run(cmd, check=True)
print(f"Built: dist/{binary_name}")

# Copy binary to package for wheel inclusion
src_binary = Path("src/airpilot") / binary_name
shutil.copy2(f"dist/{binary_name}", src_binary)
print(f"Copied to: {src_binary}")