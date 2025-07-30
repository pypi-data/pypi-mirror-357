#!/usr/bin/env python3
"""Terminal setup and management."""

import sys

# Terminal handling for Unix-like systems
try:
    import termios

    HAS_TERMIOS = True
except ImportError:
    HAS_TERMIOS = False

from .colors import colors


class TerminalManager:
    """Manages terminal setup and restoration."""

    def __init__(self):
        """Initialize terminal manager."""
        self.old_settings = None
        self.is_tty = sys.stdin.isatty() if hasattr(sys.stdin, "isatty") else False

    def setup(self) -> None:
        """Setup terminal for raw mode and enter alternate screen."""
        if not HAS_TERMIOS or not self.is_tty:
            return

        try:
            # Save current terminal settings
            self.old_settings = termios.tcgetattr(sys.stdin)
            # Set terminal to non-canonical mode (disable echo and line buffering)
            new_settings = termios.tcgetattr(sys.stdin)
            new_settings[3] = new_settings[3] & ~(termios.ECHO | termios.ICANON)
            termios.tcsetattr(sys.stdin, termios.TCSANOW, new_settings)
        except Exception:
            self.old_settings = None

        # Enter alternate screen buffer, clear and hide cursor
        print(
            f"{colors.ENTER_ALT_SCREEN}{colors.CLEAR_SCREEN}{colors.HOME}{colors.HIDE_CURSOR}",
            end="",
            flush=True,
        )

    def restore(self) -> None:
        """Restore terminal to original settings."""
        # Show cursor and exit alternate screen buffer
        print(f"{colors.SHOW_CURSOR}{colors.EXIT_ALT_SCREEN}", end="", flush=True)

        if self.old_settings and HAS_TERMIOS and self.is_tty:
            try:
                termios.tcsetattr(sys.stdin, termios.TCSANOW, self.old_settings)
            except Exception:
                pass

    def flush_input(self) -> None:
        """Flush any pending input to prevent display corruption."""
        if HAS_TERMIOS and self.is_tty:
            try:
                termios.tcflush(sys.stdin, termios.TCIFLUSH)
            except Exception:
                pass
