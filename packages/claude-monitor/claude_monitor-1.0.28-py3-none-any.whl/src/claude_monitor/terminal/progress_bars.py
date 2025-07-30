#!/usr/bin/env python3
"""Progress bar creation for terminal display."""

from .colors import colors


def create_token_progress_bar(percentage: float, width: int = 50) -> str:
    """Create a token usage progress bar with bracket style.

    Args:
        percentage: Usage percentage (0-100)
        width: Bar width in characters

    Returns:
        Formatted progress bar string
    """
    filled = int(width * percentage / 100)

    # Create the bar with green fill and red empty space
    green_bar = "█" * filled
    red_bar = "░" * (width - filled)

    return f"🟢 [{colors.GREEN}{green_bar}{colors.RED}{red_bar}{colors.RESET}] {percentage:.1f}%"


def create_time_progress_bar(
    elapsed_minutes: float, total_minutes: float, width: int = 50
) -> str:
    """Create a time progress bar showing time until reset.

    Args:
        elapsed_minutes: Minutes elapsed since start
        total_minutes: Total minutes in session
        width: Bar width in characters

    Returns:
        Formatted progress bar string with remaining time
    """
    from ..utils.time_formatter import format_time

    if total_minutes <= 0:
        percentage = 0
    else:
        percentage = min(100, (elapsed_minutes / total_minutes) * 100)

    filled = int(width * percentage / 100)

    # Create the bar with blue fill and red empty space
    blue_bar = "█" * filled
    red_bar = "░" * (width - filled)

    remaining_time = format_time(max(0, total_minutes - elapsed_minutes))
    return f"⏰ [{colors.BLUE}{blue_bar}{colors.RED}{red_bar}{colors.RESET}] {remaining_time}"
