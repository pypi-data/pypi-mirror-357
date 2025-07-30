#!/usr/bin/env python3
"""Command line argument parsing."""

import argparse
import sys


def get_version():
    """Get the current version of claude-monitor."""
    try:
        from importlib.metadata import version
        return version("claude-monitor")
    except Exception:
        return "unknown"


def parse_args():
    """Parse command line arguments.

    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description="Claude Token Monitor - Real-time token usage monitoring"
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"claude-monitor {get_version()}",
        help="Show program version and exit",
    )
    parser.add_argument(
        "--plan",
        type=str,
        default="pro",
        choices=["pro", "max5", "max20", "custom_max"],
        help='Claude plan type (default: pro). Use "custom_max" to auto-detect from highest previous block',
    )
    parser.add_argument(
        "--reset-hour", type=int, help="Change the reset hour (0-23) for daily limits"
    )
    parser.add_argument(
        "--timezone",
        type=str,
        default="Europe/Warsaw",
        help="Timezone for reset times (default: Europe/Warsaw). Examples: US/Eastern, Asia/Tokyo, UTC",
    )
    return parser.parse_args()
