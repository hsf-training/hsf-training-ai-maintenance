#!/usr/bin/env python3
"""
Main entry point for HSF Training AI Maintenance Agent.
"""

import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.cli import cli

if __name__ == "__main__":
    cli()