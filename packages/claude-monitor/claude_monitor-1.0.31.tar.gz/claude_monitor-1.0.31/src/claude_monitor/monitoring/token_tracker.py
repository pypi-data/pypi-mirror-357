#!/usr/bin/env python3
"""Token usage tracking and calculations."""

from datetime import datetime, timedelta
from typing import Any, Dict

from ..config import Config


class TokenTracker:
    """Tracks token usage and calculates predictions."""

    def __init__(self, config: Config):
        """Initialize token tracker.

        Args:
            config: Configuration object
        """
        self.config = config
        self.token_limit = None

    def update_token_limit(self, blocks=None):
        """Update token limit based on configuration and data.

        Args:
            blocks: Optional list of session blocks for custom_max calculation
        """
        if blocks:
            # When blocks are provided, always use custom_max logic
            # to find the highest historical token count
            max_tokens = 0
            for block in blocks:
                if not block.get("isGap", False) and not block.get("isActive", False):
                    tokens = block.get("totalTokens", 0)
                    if tokens > max_tokens:
                        max_tokens = tokens
            if max_tokens > 0:
                self.token_limit = max_tokens
                return

        # Fallback to config
        self.token_limit = self.config.get_token_limit(blocks)

    def get_token_limit(self) -> int:
        """Get current token limit."""
        if self.token_limit is None:
            self.update_token_limit()
        return self.token_limit

    def calculate_usage_metrics(self, active_block: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate token usage metrics.

        Args:
            active_block: Active session data

        Returns:
            Dictionary with usage metrics
        """
        tokens_used = active_block.get("totalTokens", 0)
        token_limit = self.get_token_limit()

        # Check if we need to auto-adjust limit
        if tokens_used > token_limit and self.config.plan == "pro":
            # This will be handled by the caller who has access to all blocks
            pass

        usage_percentage = (tokens_used / token_limit) * 100 if token_limit > 0 else 0
        tokens_left = token_limit - tokens_used

        return {
            "tokens_used": tokens_used,
            "token_limit": token_limit,
            "usage_percentage": usage_percentage,
            "tokens_left": tokens_left,
            "exceeds_limit": tokens_used > token_limit,
        }

    def predict_depletion(
        self,
        tokens_left: float,
        burn_rate: float,
        current_time: datetime,
        reset_time: datetime,
    ) -> datetime:
        """Predict when tokens will be depleted.

        Args:
            tokens_left: Remaining tokens
            burn_rate: Tokens per minute burn rate
            current_time: Current UTC time
            reset_time: Token reset time

        Returns:
            Predicted depletion time
        """
        if burn_rate > 0 and tokens_left > 0:
            minutes_to_depletion = tokens_left / burn_rate
            return current_time + timedelta(minutes=minutes_to_depletion)
        else:
            # If no burn rate or tokens already depleted, use reset time
            return reset_time

    def should_show_custom_max_switch(self, tokens_used: int) -> bool:
        """Check if we should show the custom_max switch notification.

        Args:
            tokens_used: Current token usage

        Returns:
            True if notification should be shown
        """
        original_limit = self.config.TOKEN_LIMITS.get(self.config.plan, 7000)
        return (
            tokens_used > original_limit
            and self.config.plan != "custom_max"
            and self.token_limit > original_limit
        )
