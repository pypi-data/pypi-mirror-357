#!/usr/bin/env python3
"""Load environment variables from .env file for development."""

import os
from pathlib import Path


def load_env() -> None:
    """Load environment variables from .env file if it exists."""
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()


if __name__ == "__main__":
    load_env()
    print("Environment variables loaded from .env")

    # Show current PoC license
    poc_license = os.getenv("AIRPILOT_POC_LICENSE", "Not set")
    print(f"AIRPILOT_POC_LICENSE: {poc_license}")
