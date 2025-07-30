#!/usr/bin/env python3
"""Alert and notification management."""

from datetime import datetime
from typing import Any, Dict, List

from ..terminal.colors import colors


class AlertManager:
    """Manages alerts and notifications."""

    def __init__(self):
        """Initialize alert manager."""
        self.alerts = []

    def clear(self):
        """Clear all alerts."""
        self.alerts = []

    def add_custom_max_switch(self, token_limit: int):
        """Add notification for switching to custom_max plan.

        Args:
            token_limit: New token limit
        """
        self.alerts.append(
            f"🔄 {colors.YELLOW}Tokens exceeded plan limit - switched to custom_max ({token_limit:,}){colors.RESET}"
        )

    def add_token_exceeded(self, tokens_used: int, token_limit: int):
        """Add notification for exceeding token limit.

        Args:
            tokens_used: Current token usage
            token_limit: Token limit
        """
        self.alerts.append(
            f"🚨 {colors.RED}TOKENS EXCEEDED MAX LIMIT! ({tokens_used:,} > {token_limit:,}){colors.RESET}"
        )

    def add_depletion_warning(self):
        """Add warning that tokens will run out before reset."""
        self.alerts.append(
            f"⚠️  {colors.RED}Tokens will run out BEFORE reset!{colors.RESET}"
        )

    def check_alerts(
        self,
        usage_metrics: Dict[str, Any],
        predicted_end: datetime,
        reset_time: datetime,
        show_switch: bool,
    ) -> None:
        """Check conditions and add appropriate alerts.

        Args:
            usage_metrics: Token usage metrics
            predicted_end: Predicted token depletion time
            reset_time: Token reset time
            show_switch: Whether to show custom_max switch notification
        """
        self.clear()

        if show_switch:
            self.add_custom_max_switch(usage_metrics["token_limit"])

        if usage_metrics["exceeds_limit"]:
            self.add_token_exceeded(
                usage_metrics["tokens_used"], usage_metrics["token_limit"]
            )

        if predicted_end < reset_time:
            self.add_depletion_warning()

    def get_alerts(self) -> List[str]:
        """Get all current alerts.

        Returns:
            List of alert messages
        """
        return self.alerts.copy()
