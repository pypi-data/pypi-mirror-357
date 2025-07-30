#!/usr/bin/env python3
"""Session data handling and parsing."""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from ..config import Config


class SessionManager:
    """Manages session data extraction and processing."""

    def __init__(self, config: Config):
        """Initialize session manager.

        Args:
            config: Configuration object
        """
        self.config = config

    def find_active_session(
        self, blocks: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Find the active session from blocks.

        Args:
            blocks: List of session blocks

        Returns:
            Active session block or None
        """
        for block in blocks:
            if block.get("isActive", False):
                return block
        return None

    def parse_session_times(self, active_block: Dict[str, Any]) -> Dict[str, Any]:
        """Parse time information from active session block.

        Args:
            active_block: Active session data

        Returns:
            Dictionary with parsed time information
        """
        result = {
            "start_time": None,
            "reset_time": None,
            "current_time": datetime.now(Config.UTC_TZ),
            "has_valid_times": False,
        }

        # Parse start time
        start_time_str = active_block.get("startTime")
        if start_time_str:
            start_time = datetime.fromisoformat(start_time_str.replace("Z", "+00:00"))
            # Ensure start_time is in UTC
            if start_time.tzinfo is None:
                start_time = Config.UTC_TZ.localize(start_time)
            else:
                start_time = start_time.astimezone(Config.UTC_TZ)
            result["start_time"] = start_time

        # Parse end time (reset time)
        end_time_str = active_block.get("endTime")
        if end_time_str:
            reset_time = datetime.fromisoformat(end_time_str.replace("Z", "+00:00"))
            # Ensure reset_time is in UTC
            if reset_time.tzinfo is None:
                reset_time = Config.UTC_TZ.localize(reset_time)
            else:
                reset_time = reset_time.astimezone(Config.UTC_TZ)
            result["reset_time"] = reset_time
        else:
            # Fallback: if no endTime, estimate 5 hours from startTime
            if result["start_time"]:
                result["reset_time"] = result["start_time"] + timedelta(hours=5)
            else:
                result["reset_time"] = result["current_time"] + timedelta(hours=5)

        result["has_valid_times"] = bool(start_time_str and end_time_str)
        return result

    def calculate_session_progress(self, time_info: Dict[str, Any]) -> Dict[str, float]:
        """Calculate session progress metrics.

        Args:
            time_info: Parsed time information

        Returns:
            Dictionary with progress metrics
        """
        start_time = time_info["start_time"]
        reset_time = time_info["reset_time"]
        current_time = time_info["current_time"]

        # Calculate time to reset
        time_to_reset = reset_time - current_time
        minutes_to_reset = time_to_reset.total_seconds() / 60

        # Calculate session progress
        if start_time and time_info["has_valid_times"]:
            total_session_minutes = (reset_time - start_time).total_seconds() / 60
            elapsed_session_minutes = (current_time - start_time).total_seconds() / 60
            elapsed_session_minutes = max(0, elapsed_session_minutes)
        else:
            # Fallback to 5 hours if times not available
            total_session_minutes = 300
            elapsed_session_minutes = max(0, 300 - minutes_to_reset)

        return {
            "minutes_to_reset": minutes_to_reset,
            "total_session_minutes": total_session_minutes,
            "elapsed_session_minutes": elapsed_session_minutes,
        }
