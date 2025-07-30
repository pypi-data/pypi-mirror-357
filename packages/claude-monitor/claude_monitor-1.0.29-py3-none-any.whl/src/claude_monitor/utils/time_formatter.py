#!/usr/bin/env python3
"""Time formatting utilities."""


def format_time(minutes: float) -> str:
    """Format minutes into human-readable time (e.g., '3h 45m').

    Args:
        minutes: Number of minutes to format

    Returns:
        Formatted time string
    """
    if minutes < 60:
        return f"{int(minutes)}m"
    hours = int(minutes // 60)
    mins = int(minutes % 60)
    if mins == 0:
        return f"{hours}h"
    return f"{hours}h {mins}m"
