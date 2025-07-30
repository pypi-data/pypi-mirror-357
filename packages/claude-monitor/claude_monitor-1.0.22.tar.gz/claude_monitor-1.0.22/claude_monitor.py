#!/usr/bin/env python3
"""Entry point for Claude Monitor - redirects to the refactored package."""

# from src.usage_analyzer import api
#
# if __name__ == "__main__":
#     api.analyze_usage()

from src.claude_monitor import main

if __name__ == "__main__":
    main()
