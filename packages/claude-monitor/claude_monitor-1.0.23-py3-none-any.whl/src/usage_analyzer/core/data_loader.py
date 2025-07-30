"""
Simplified Data Loading for Claude Usage Analysis

Basic data loader that parses Claude usage data from JSONL files.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

from src.usage_analyzer.core.limit_detector import LimitDetector
from src.usage_analyzer.models.data_structures import CostMode, LimitMessage, UsageEntry
from src.usage_analyzer.utils.path_discovery import discover_claude_data_paths
from src.usage_analyzer.utils.pricing_fetcher import ClaudePricingFetcher


class DataLoader:
    """Simplified data loading component for Claude usage data."""

    def __init__(self, data_path: Optional[str] = None):
        """Initialize the data loader."""
        if data_path is None:
            # Auto-discover
            paths = discover_claude_data_paths()
            self.data_path = (
                paths[0] if paths else Path("~/.claude/projects").expanduser()
            )
        else:
            self.data_path = Path(data_path).expanduser()

        self.pricing_fetcher = ClaudePricingFetcher()
        self.limit_detector = LimitDetector()

    def load_usage_data(
        self, mode: CostMode = CostMode.AUTO
    ) -> Tuple[List[UsageEntry], List[LimitMessage]]:
        """Load and process all usage data."""
        # Find JSONL files
        jsonl_files = self._find_jsonl_files()

        if not jsonl_files:
            return [], []

        all_entries: List[UsageEntry] = []
        all_limit_messages: List[LimitMessage] = []
        # Track processed message+request combinations for deduplication
        processed_hashes = set()

        # Track overall statistics
        total_files = len(jsonl_files)
        total_processed = 0

        # Process each file
        for file_path in jsonl_files:
            entries, limit_messages = self._parse_jsonl_file(
                file_path, processed_hashes, mode
            )
            all_entries.extend(entries)
            all_limit_messages.extend(limit_messages)
            total_processed += 1

        # print(f"Loaded {len(all_entries)} entries from {total_processed} files")
        # print(f"Deduplication: {len(processed_hashes)} unique message+request combinations processed")

        # Sort chronologically
        return (
            sorted(all_entries, key=lambda e: e.timestamp),
            sorted(all_limit_messages, key=lambda m: m.timestamp),
        )

    def _find_jsonl_files(self) -> List[Path]:
        """Find all .jsonl files in the data directory."""
        if not self.data_path.exists():
            return []

        return list(self.data_path.rglob("*.jsonl"))

    def _parse_jsonl_file(
        self, file_path: Path, processed_hashes: set, mode: CostMode
    ) -> Tuple[List[UsageEntry], List[LimitMessage]]:
        """Parse a single JSONL file with deduplication."""
        entries = []
        limit_messages = []
        total_lines = 0
        skipped_duplicates = 0
        skipped_synthetic = 0
        skipped_invalid = 0

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    total_lines += 1

                    try:
                        data = json.loads(line)

                        # Check for limit messages first
                        limit_message = self.limit_detector.detect_token_limit_messages(
                            data
                        )
                        if limit_message:
                            limit_messages.append(limit_message)

                        # Check for duplicate message + request ID combination
                        unique_hash = self._create_unique_hash(data)
                        if unique_hash and unique_hash in processed_hashes:
                            # Skip duplicate message
                            skipped_duplicates += 1
                            continue

                        entry = self._convert_to_usage_entry(data, mode)
                        if entry:
                            entries.append(entry)
                            # Mark this combination as processed
                            if unique_hash:
                                processed_hashes.add(unique_hash)
                        else:
                            # Entry was None - invalid data
                            skipped_invalid += 1

                    except (json.JSONDecodeError, Exception):
                        skipped_invalid += 1
                        continue

        except Exception:
            pass

        # Print debug info for this file (comment out for production)
        # print(f"File: {file_path.name}")
        # print(f"  Total lines: {total_lines}")
        # print(f"  Valid entries: {len(entries)}")
        # print(f"  Skipped duplicates: {skipped_duplicates}")
        # print(f"  Skipped synthetic: {skipped_synthetic}")
        # print(f"  Skipped invalid: {skipped_invalid}")
        # print()

        return entries, limit_messages

    def _create_unique_hash(self, data: dict) -> Optional[str]:
        """Create a unique identifier for deduplication using message ID and request ID."""
        # Try to get message ID from different possible locations
        message_id = None
        request_id = data.get("requestId") or data.get("request_id")

        # Check different message structures
        if "message" in data and isinstance(data["message"], dict):
            message_id = data["message"].get("id")
        else:
            message_id = data.get("message_id")

        if message_id is None or request_id is None:
            return None

        # Create a hash using simple concatenation
        return f"{message_id}:{request_id}"

    def _convert_to_usage_entry(
        self, data: dict, mode: CostMode
    ) -> Optional[UsageEntry]:
        """Convert raw data to UsageEntry with proper cost calculation based on mode."""
        try:
            if "timestamp" not in data:
                return None

            timestamp = datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))

            # Handle both nested and flat usage data
            usage = data.get("usage", {})
            if not usage:
                # Try extracting from message structure
                message = data.get("message", {})
                usage = message.get("usage", {})

            # Extract token counts
            input_tokens = usage.get("input_tokens", 0) or 0
            output_tokens = usage.get("output_tokens", 0) or 0
            cache_creation_tokens = usage.get("cache_creation_input_tokens", 0) or 0
            cache_read_tokens = usage.get("cache_read_input_tokens", 0) or 0

            # Create entry data for cost calculation
            entry_data = {
                "model": data.get("model", "")
                or (data.get("message", {}).get("model", "")),
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cache_creation_tokens": cache_creation_tokens,
                "cache_read_tokens": cache_read_tokens,
                "costUSD": data.get("cost") or data.get("costUSD"),
            }

            # Calculate cost using the new cost calculation logic
            cost_usd = self.pricing_fetcher.calculateCostForEntry(entry_data, mode)

            return UsageEntry(
                timestamp=timestamp,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cache_creation_tokens=cache_creation_tokens,
                cache_read_tokens=cache_read_tokens,
                cost_usd=cost_usd,
                model=entry_data["model"],
                message_id=data.get("message_id")
                or (data.get("message", {}).get("id")),
                request_id=data.get("request_id"),
            )
        except Exception:
            return None
