#!/usr/bin/env python3
"""Color management for terminal output."""

from dataclasses import dataclass


@dataclass
class Colors:
    """Terminal color codes."""

    # Basic colors
    RESET = "\033[0m"

    # Bright colors
    CYAN = "\033[96m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    WHITE = "\033[97m"
    GRAY = "\033[90m"

    # Control sequences
    CLEAR_SCREEN = "\033[2J"
    HOME = "\033[H"
    HIDE_CURSOR = "\033[?25l"
    SHOW_CURSOR = "\033[?25h"
    ENTER_ALT_SCREEN = "\033[?1049h"
    EXIT_ALT_SCREEN = "\033[?1049l"
    CLEAR_TO_END = "\033[J"

    @classmethod
    def strip_colors(cls, text: str) -> str:
        """Remove all ANSI color codes from text."""
        import re

        ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
        return ansi_escape.sub("", text)


# Default color instance
colors = Colors()
