#!/usr/bin/env python3
"""
Allow running the config_manager module directly:
python -m config_manager
"""

import sys
from .cli import main

if __name__ == "__main__":
    sys.exit(main())