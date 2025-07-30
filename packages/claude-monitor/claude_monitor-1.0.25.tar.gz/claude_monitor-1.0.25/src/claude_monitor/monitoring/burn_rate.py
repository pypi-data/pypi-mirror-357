#!/usr/bin/env python3
"""Burn rate calculation for token usage."""

from datetime import datetime, timedelta
from typing import Any, Dict, List

from ..config import Config


def get_velocity_indicator(burn_rate: float) -> str:
    """Get velocity emoji based on burn rate.

    Args:
        burn_rate: Tokens per minute burn rate

    Returns:
        Emoji indicator for the burn rate
    """
    if burn_rate < 50:
        return "🐌"  # Slow
    elif burn_rate < 150:
        return "➡️"  # Normal
    elif burn_rate < 300:
        return "🚀"  # Fast
    else:
        return "⚡"  # Very fast


def calculate_hourly_burn_rate(
    blocks: List[Dict[str, Any]], current_time: datetime
) -> float:
    """Calculate burn rate based on all sessions in the last hour.

    Args:
        blocks: List of session blocks
        current_time: Current UTC time

    Returns:
        Tokens per minute burn rate
    """
    if not blocks:
        return 0

    one_hour_ago = current_time - timedelta(hours=1)
    total_tokens = 0

    for block in blocks:
        start_time_str = block.get("startTime")
        if not start_time_str:
            continue

        # Parse start time - data from usage_analyzer is in UTC
        try:
            start_time = datetime.fromisoformat(start_time_str.replace("Z", "+00:00"))
            # Ensure it's in UTC for calculations
            if start_time.tzinfo is None:
                start_time = Config.UTC_TZ.localize(start_time)
            else:
                start_time = start_time.astimezone(Config.UTC_TZ)
        except (ValueError, TypeError):
            continue

        # Skip gaps
        if block.get("isGap", False):
            continue

        # Determine session end time
        if block.get("isActive", False):
            # For active sessions, use current time
            session_actual_end = current_time
        else:
            # For completed sessions, use actualEndTime, endTime, or current time
            actual_end_str = block.get("actualEndTime") or block.get("endTime")
            if actual_end_str:
                try:
                    session_actual_end = datetime.fromisoformat(
                        actual_end_str.replace("Z", "+00:00")
                    )
                    # Ensure it's in UTC for calculations
                    if session_actual_end.tzinfo is None:
                        session_actual_end = Config.UTC_TZ.localize(session_actual_end)
                    else:
                        session_actual_end = session_actual_end.astimezone(
                            Config.UTC_TZ
                        )
                except (ValueError, TypeError):
                    session_actual_end = current_time
            else:
                session_actual_end = current_time

        # Check if session overlaps with the last hour
        if session_actual_end < one_hour_ago:
            # Session ended before the last hour
            continue

        # Calculate how much of this session falls within the last hour
        session_start_in_hour = max(start_time, one_hour_ago)
        session_end_in_hour = min(session_actual_end, current_time)

        if session_end_in_hour <= session_start_in_hour:
            continue

        # Calculate portion of tokens used in the last hour
        total_session_duration = (
            session_actual_end - start_time
        ).total_seconds() / 60  # minutes
        hour_duration = (
            session_end_in_hour - session_start_in_hour
        ).total_seconds() / 60  # minutes

        if total_session_duration > 0:
            session_tokens = block.get("totalTokens", 0)
            tokens_in_hour = session_tokens * (hour_duration / total_session_duration)
            total_tokens += tokens_in_hour

    # Return tokens per minute
    return total_tokens / 60 if total_tokens > 0 else 0
