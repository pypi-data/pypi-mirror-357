#!/usr/bin/env python3
"""Main orchestration module for Claude Monitor."""

import sys
import threading

from src.usage_analyzer.api import analyze_usage, analyze_usage_first

from .config import Config
from .monitoring.alerts import AlertManager
from .monitoring.burn_rate import calculate_hourly_burn_rate
from .monitoring.session import SessionManager
from .monitoring.token_tracker import TokenTracker
from .terminal import colors
from .terminal.display import Display
from .terminal.manager import TerminalManager
from .utils.argparser import parse_args


class Monitor:
    """Main monitoring orchestrator."""

    def __init__(self, config: Config):
        """Initialize monitor with configuration.

        Args:
            config: Configuration object
        """
        self.config = config
        self.display = Display(config)
        self.session_manager = SessionManager(config)
        self.token_tracker = TokenTracker(config)
        self.alert_manager = AlertManager()
        self.stop_event = threading.Event()

    def fetch_data(self):
        """Fetch usage data from API.

        Returns:
            API response data or None
        """
        return analyze_usage(plan=self.config.plan, timezone=self.config.timezone)

    def process_no_session(self):
        """Handle case when no active session is found."""
        self.display.show_no_session(self.token_tracker.get_token_limit())

    def process_active_session(self, data, active_block):
        """Process and display active session data.

        Args:
            data: Full API response data
            active_block: Active session block
        """
        # Get usage metrics
        usage_metrics = self.token_tracker.calculate_usage_metrics(active_block)

        # Check if we need to auto-adjust limit for custom_max
        if usage_metrics["tokens_used"] > usage_metrics["token_limit"]:
            self.token_tracker.update_token_limit(data["blocks"])
            usage_metrics = self.token_tracker.calculate_usage_metrics(active_block)

        # Get time information
        time_info = self.session_manager.parse_session_times(active_block)
        progress = self.session_manager.calculate_session_progress(time_info)

        # Calculate burn rate
        burn_rate = calculate_hourly_burn_rate(
            data["blocks"], time_info["current_time"]
        )

        # Predict depletion
        predicted_end = self.token_tracker.predict_depletion(
            usage_metrics["tokens_left"],
            burn_rate,
            time_info["current_time"],
            time_info["reset_time"],
        )

        # Check alerts
        show_switch = self.token_tracker.should_show_custom_max_switch(
            usage_metrics["tokens_used"]
        )
        self.alert_manager.check_alerts(
            usage_metrics, predicted_end, time_info["reset_time"], show_switch
        )

        # Prepare display data
        display_data = {
            "usage_percentage": usage_metrics["usage_percentage"],
            "elapsed_minutes": progress["elapsed_session_minutes"],
            "total_minutes": progress["total_session_minutes"],
            "tokens_used": usage_metrics["tokens_used"],
            "token_limit": usage_metrics["token_limit"],
            "tokens_left": usage_metrics["tokens_left"],
            "burn_rate": burn_rate,
            "predicted_end": predicted_end,
            "reset_time": time_info["reset_time"],
            "alerts": self.alert_manager.get_alerts(),
        }

        self.display.show_active_session(display_data)

    def run_loop(self):
        """Run the main monitoring loop."""
        # Show loading screen immediately
        self.display.show_loading()

        while not self.stop_event.is_set():
            # Fetch data
            data = self.fetch_data()

            if not data or "blocks" not in data:
                self.display.show_error()
                self.stop_event.wait(timeout=self.config.REFRESH_INTERVAL)
                continue

            # Find active session
            active_block = self.session_manager.find_active_session(data["blocks"])

            if not active_block:
                self.process_no_session()
            else:
                self.process_active_session(data, active_block)

            # Wait for refresh interval
            self.stop_event.wait(timeout=self.config.REFRESH_INTERVAL)

    def stop(self):
        """Stop the monitoring loop."""
        self.stop_event.set()


def handle_custom_max_initialization(config: Config):
    """Handle initialization for custom_max plan.

    Args:
        config: Configuration object

    Returns:
        Updated token tracker with custom limit
    """
    tracker = TokenTracker(config)

    if config.plan != "custom_max":
        return tracker

    print(
        f"{colors.CYAN}Fetching initial data to determine custom max token limit...{colors.RESET}"
    )
    initial_data = analyze_usage(plan=config.plan, timezone=config.timezone)

    if initial_data and "blocks" in initial_data:
        tracker.update_token_limit(initial_data["blocks"])
        token_limit = tracker.get_token_limit()
        print(
            f"{colors.CYAN}Custom max token limit detected: {token_limit:,}{colors.RESET}"
        )
    else:
        print(
            f"{colors.YELLOW}Failed to fetch data, falling back to Pro limit: "
            f"{tracker.get_token_limit():,}{colors.RESET}"
        )

    return tracker


def main():
    """Main entry point for Claude Monitor."""
    # Check for updates first
    # Parse arguments
    args = parse_args()

    # Create configuration
    config = Config(plan=args.plan, reset_hour=args.reset_hour, timezone=args.timezone)

    analyze_usage_first(config.plan, config.timezone)
    # Initialize terminal manager
    terminal = TerminalManager()

    # Create monitor
    monitor = Monitor(config)

    # Handle custom_max initialization if needed
    if config.plan == "custom_max":
        tracker = handle_custom_max_initialization(config)
        monitor.token_tracker = tracker

    try:
        # Setup terminal
        terminal.setup()

        # Run monitoring loop
        monitor.run_loop()

    except KeyboardInterrupt:
        # Stop monitoring
        monitor.stop()

        # Restore terminal
        terminal.restore()

        # Show exit message
        monitor.display.show_exit_message()
        sys.exit(0)

    except Exception as e:
        # Restore terminal on any error
        terminal.restore()
        print(f"\n\nError: {e}")
        raise


if __name__ == "__main__":
    main()
