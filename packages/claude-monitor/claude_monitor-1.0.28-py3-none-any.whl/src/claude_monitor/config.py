#!/usr/bin/env python3
"""Configuration module for Claude Monitor."""

import os
from dataclasses import dataclass
from typing import Dict, Optional

import pytz


@dataclass
class Config:
    """Configuration for Claude Monitor."""

    # Plan configurations
    plan: str = "pro"
    reset_hour: Optional[int] = None
    timezone: str = "Europe/Warsaw"

    # Token limits by plan
    TOKEN_LIMITS: Dict[str, int] = None

    # Timing
    REFRESH_INTERVAL: float = 3.0

    # Display settings
    PROGRESS_BAR_WIDTH: int = 50
    MAX_OUTPUT_CHARS: int = 30000

    # Timezone
    UTC_TZ = pytz.UTC

    def __post_init__(self):
        """Initialize computed fields."""
        self.TOKEN_LIMITS = {"pro": 44000, "max5": 220000, "max20": 880000}

        # Override from environment if available
        if env_plan := os.getenv("CLAUDE_MONITOR_PLAN"):
            self.plan = env_plan
        if env_tz := os.getenv("CLAUDE_MONITOR_TIMEZONE"):
            self.timezone = env_tz
        if env_reset := os.getenv("CLAUDE_MONITOR_RESET_HOUR"):
            try:
                self.reset_hour = int(env_reset)
            except ValueError:
                pass

    def get_token_limit(self, blocks=None):
        """Get token limit based on plan type."""
        if self.plan == "custom_max" and blocks:
            # Find the highest token count from all previous blocks
            max_tokens = 0
            for block in blocks:
                if not block.get("isGap", False) and not block.get("isActive", False):
                    tokens = block.get("totalTokens", 0)
                    if tokens > max_tokens:
                        max_tokens = tokens
            # Return the highest found, or default to pro if none found
            return max_tokens if max_tokens > 0 else self.TOKEN_LIMITS["pro"]

        return self.TOKEN_LIMITS.get(self.plan, self.TOKEN_LIMITS["pro"])

    def get_display_timezone(self):
        """Get the timezone for display purposes."""
        try:
            return pytz.timezone(self.timezone)
        except pytz.exceptions.UnknownTimeZoneError:
            return pytz.timezone("Europe/Warsaw")
