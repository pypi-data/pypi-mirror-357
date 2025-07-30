"""
Token Limit Detection for Claude Usage Analysis

Detects "limit reached" messages in JSONL data and categorizes them by type.
"""

import re
from datetime import datetime
from typing import Any, Dict, Optional

from src.usage_analyzer.models.data_structures import LimitMessage


class LimitDetector:
    """Detects token limit messages in Claude usage data."""

    def detect_token_limit_messages(
        self, raw_data: Dict[str, Any]
    ) -> Optional[LimitMessage]:
        """
        Detect token limit messages from JSONL entries with safe parsing.

        Only processes:
        1. System messages (type: "system")
        2. Tool results in user messages (type: "user" with tool_result)
        3. Assistant messages with synthetic model (type: "assistant" with model: "<synthetic>")

        Args:
            raw_data: Raw JSONL entry data

        Returns:
            LimitMessage if detected, None otherwise
        """
        entry_type = raw_data.get("type")

        # Case 1: System messages
        if entry_type == "system":
            content = raw_data.get("content", "")
            if isinstance(content, str) and "limit reached" in content.lower():
                timestamp_str = raw_data.get("timestamp")
                if not timestamp_str:
                    return None
                timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                return self._create_limit_message(content, timestamp)

        # Case 2: User messages with tool results
        elif entry_type == "user":
            message = raw_data.get("message", {})
            if isinstance(message, dict):
                content = message.get("content", [])
                if isinstance(content, list):
                    for item in content:
                        if isinstance(item, dict) and item.get("type") == "tool_result":
                            text = item.get("text", "")
                            if (
                                isinstance(text, str)
                                and "limit reached" in text.lower()
                            ):
                                timestamp_str = raw_data.get("timestamp")
                                if not timestamp_str:
                                    continue
                                timestamp = datetime.fromisoformat(
                                    timestamp_str.replace("Z", "+00:00")
                                )
                                return self._create_limit_message_with_reset(
                                    text, timestamp
                                )

        # Case 3: Assistant messages with synthetic model
        elif entry_type == "assistant":
            message = raw_data.get("message", {})
            if isinstance(message, dict):
                model = message.get("model", "")
                if model == "<synthetic>":
                    content = message.get("content", "")
                    # Handle both string and list content
                    text_content = ""
                    if isinstance(content, str):
                        text_content = content
                    elif isinstance(content, list):
                        for item in content:
                            if isinstance(item, dict) and item.get("type") == "text":
                                text_content = item.get("text", "")
                                break

                    if text_content and "limit reached" in text_content.lower():
                        timestamp_str = raw_data.get("timestamp")
                        if not timestamp_str:
                            return None
                        timestamp = datetime.fromisoformat(
                            timestamp_str.replace("Z", "+00:00")
                        )
                        return self._create_limit_message_with_reset(
                            text_content, timestamp
                        )

        return None

    def _create_limit_message(self, content: str, timestamp: datetime) -> LimitMessage:
        """Create limit message for system messages."""
        content_lower = content.lower()

        # Check for Opus limit (informational - session continues with Sonnet)
        if "claude opus" in content_lower and "limit reached" in content_lower:
            return LimitMessage(
                type="opus_limit", timestamp=timestamp, content=content, reset_time=None
            )

        # General limit (ends session)
        return LimitMessage(
            type="general_limit", timestamp=timestamp, content=content, reset_time=None
        )

    def _create_limit_message_with_reset(
        self, text: str, timestamp: datetime
    ) -> LimitMessage:
        """Create limit message with reset time parsing for tool results."""
        text_lower = text.lower()

        # Parse reset time from format: "Claude AI usage limit reached|1750352400"
        reset_time = None
        match = re.search(r"limit reached\|(\d+)", text)
        if match:
            try:
                unix_timestamp = int(match.group(1))
                # Use UTC timezone for Unix timestamp
                from datetime import timezone

                reset_time = datetime.fromtimestamp(unix_timestamp, tz=timezone.utc)
            except (ValueError, OSError):
                pass

        # Check for Opus limit
        if "claude opus" in text_lower and "limit reached" in text_lower:
            return LimitMessage(
                type="opus_limit",
                timestamp=timestamp,
                content=text,
                reset_time=reset_time,
            )

        # General limit (ends session)
        return LimitMessage(
            type="general_limit",
            timestamp=timestamp,
            content=text,
            reset_time=reset_time,
        )
