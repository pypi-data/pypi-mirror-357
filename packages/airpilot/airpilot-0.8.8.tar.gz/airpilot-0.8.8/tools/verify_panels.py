#!/usr/bin/env python3

"""
Verification script to test Python panel outputs
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from airpilot.ui.panels import (
    show_sync_panel,
    show_main_help_panel,
    show_license_help_panel,
    show_scaffolding_panel,
    show_license_status_panel
)

print('\n=== PYTHON PANELS OUTPUT ===\n')

print('Testing show_sync_panel():')
show_sync_panel()

print('\n\nTesting show_main_help_panel():')
show_main_help_panel()

print('\n\nTesting show_license_help_panel():')
show_license_help_panel()

print('\n\nTesting show_scaffolding_panel():')
show_scaffolding_panel(Path('/test/path/.air'))

print('\n\nTesting show_license_status_panel():')
show_license_status_panel({
    'plan': 'poc',
    'licensed': True,
    'features': ['init', 'sync', 'cloud']
})

print('\n\n=== VERIFICATION COMPLETE ===\n')