#!/usr/bin/env python3
"""Display management for terminal output."""

from datetime import datetime
from typing import Any, Dict

from ..monitoring.burn_rate import get_velocity_indicator
from .colors import colors
from .progress_bars import create_time_progress_bar, create_token_progress_bar


class Display:
    """Manages screen display and rendering."""

    def __init__(self, config):
        """Initialize display.

        Args:
            config: Configuration object
        """
        self.config = config
        self.screen_buffer = []

    def clear_buffer(self):
        """Clear the screen buffer."""
        self.screen_buffer = []

    def add_line(self, line: str = ""):
        """Add a line to the screen buffer."""
        self.screen_buffer.append(line)

    def render(self):
        """Render the screen buffer to terminal."""
        # Build complete screen output
        output = (
            colors.CLEAR_SCREEN + "\n".join(self.screen_buffer) + colors.CLEAR_TO_END
        )
        print(output, end="", flush=True)

    def show_header(self):
        """Add stylized header to buffer."""
        # Sparkle pattern
        sparkles = f"{colors.CYAN}✦ ✧ ✦ ✧ {colors.RESET}"

        self.add_line(colors.HOME)  # Home position
        self.add_line(
            f"{sparkles}{colors.CYAN}CLAUDE CODE USAGE MONITOR{colors.RESET} {sparkles}"
        )
        self.add_line(f"{colors.BLUE}{'=' * 60}{colors.RESET}")
        self.add_line(
            f"{colors.GRAY}[ {self.config.plan} | {self.config.timezone} ]{colors.RESET}"
        )
        self.add_line()

    def show_loading(self):
        """Display loading screen."""
        self.clear_buffer()
        self.show_header()
        self.add_line()
        self.add_line(f"{colors.CYAN}⏳ Loading...{colors.RESET}")
        self.add_line()
        self.add_line(f"{colors.YELLOW}Fetching Claude usage data...{colors.RESET}")
        self.add_line()
        self.add_line(f"{colors.GRAY}This may take a few seconds{colors.RESET}")
        self.render()

    def show_error(self, message: str = None):
        """Display error screen.

        Args:
            message: Optional custom error message
        """
        self.clear_buffer()
        self.show_header()

        if message:
            self.add_line(f"{colors.RED}{message}{colors.RESET}")
        else:
            self.add_line(f"{colors.RED}Failed to get usage data{colors.RESET}")
            self.add_line()
            self.add_line(f"{colors.YELLOW}Possible causes:{colors.RESET}")
            self.add_line("  • You're not logged into Claude")
            self.add_line("  • Network connection issues")

        self.add_line()
        self.add_line(
            f"{colors.GRAY}Retrying in 3 seconds... (Ctrl+C to exit){colors.RESET}"
        )
        self.render()

    def show_no_session(self, token_limit: int):
        """Display when no active session found.

        Args:
            token_limit: Token limit to display
        """
        self.clear_buffer()
        self.show_header()

        # Empty progress bar
        self.add_line(
            f"📊 {colors.WHITE}Token Usage:{colors.RESET}    {create_token_progress_bar(0.0)}"
        )
        self.add_line()

        # Token stats
        self.add_line(
            f"🎯 {colors.WHITE}Tokens:{colors.RESET}         {colors.WHITE}0{colors.RESET} / "
            f"{colors.GRAY}~{token_limit:,}{colors.RESET} ({colors.CYAN}0 left{colors.RESET})"
        )
        self.add_line(
            f"🔥 {colors.WHITE}Burn Rate:{colors.RESET}      {colors.YELLOW}0.0{colors.RESET} "
            f"{colors.GRAY}tokens/min{colors.RESET}"
        )
        self.add_line()

        # Status line
        current_time = datetime.now(self.config.get_display_timezone())
        current_time_str = current_time.strftime("%H:%M:%S")
        self.add_line(
            f"⏰ {colors.GRAY}{current_time_str}{colors.RESET} 📝 "
            f"{colors.CYAN}No active session{colors.RESET} | "
            f"{colors.GRAY}Ctrl+C to exit{colors.RESET} 🟨"
        )
        self.render()

    def show_active_session(self, data: Dict[str, Any]):
        """Display active session monitoring.

        Args:
            data: Dictionary containing all display data
        """
        self.clear_buffer()
        self.show_header()

        # Token usage bar
        self.add_line(
            f"📊 {colors.WHITE}Token Usage:{colors.RESET}    "
            f"{create_token_progress_bar(data['usage_percentage'])}"
        )
        self.add_line()

        # Time to reset bar
        self.add_line(
            f"⏳ {colors.WHITE}Time to Reset:{colors.RESET}  "
            f"{create_time_progress_bar(data['elapsed_minutes'], data['total_minutes'])}"
        )
        self.add_line()

        # Token stats
        self.add_line(
            f"🎯 {colors.WHITE}Tokens:{colors.RESET}         "
            f"{colors.WHITE}{data['tokens_used']:,}{colors.RESET} / "
            f"{colors.GRAY}~{data['token_limit']:,}{colors.RESET} "
            f"({colors.CYAN}{data['tokens_left']:,} left{colors.RESET})"
        )

        # Burn rate with velocity indicator
        velocity = get_velocity_indicator(data["burn_rate"])
        self.add_line(
            f"🔥 {colors.WHITE}Burn Rate:{colors.RESET}      "
            f"{colors.YELLOW}{data['burn_rate']:.1f}{colors.RESET} "
            f"{colors.GRAY}tokens/min{colors.RESET} {velocity}"
        )
        self.add_line()

        # Predictions
        display_tz = self.config.get_display_timezone()
        predicted_end_str = (
            data["predicted_end"].astimezone(display_tz).strftime("%H:%M")
        )
        reset_time_str = data["reset_time"].astimezone(display_tz).strftime("%H:%M")

        self.add_line(
            f"🏁 {colors.WHITE}Predicted End:{colors.RESET} {predicted_end_str}"
        )
        self.add_line(f"🔄 {colors.WHITE}Token Reset:{colors.RESET}   {reset_time_str}")
        self.add_line()

        # Alerts
        for alert in data.get("alerts", []):
            self.add_line(alert)
            self.add_line()

        # Status line
        current_time = datetime.now(display_tz)
        current_time_str = current_time.strftime("%H:%M:%S")
        self.add_line(
            f"⏰ {colors.GRAY}{current_time_str}{colors.RESET} 📝 "
            f"{colors.CYAN}Smooth sailing...{colors.RESET} | "
            f"{colors.GRAY}Ctrl+C to exit{colors.RESET} 🟨"
        )

        self.render()

    def show_exit_message(self):
        """Display exit message."""
        print(f"\n\n{colors.CYAN}Monitoring stopped.{colors.RESET}")
