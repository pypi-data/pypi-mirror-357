#!/usr/bin/env python3
"""Claude Code Usage Monitor - Curses-based terminal UI."""

import argparse
import curses
import json
import os
import subprocess
import sys
import threading
import time
from datetime import datetime, timedelta

import pytz

from check_dependency import test_node, test_npx


class TokenMonitor:
    """Main application class for token monitoring with curses UI."""
    
    def __init__(self, stdscr, args):
        self.stdscr = stdscr
        self.args = args
        self.running = True
        self.data_lock = threading.Lock()
        self.current_data = None
        self.token_limit = 7000  # Default
        self.last_update_time = 0
        self.screen_update_interval = 0.5  # Update screen every 0.5 seconds
        self.data_changed = True  # Flag to track if data changed
        self._last_active_state = None  # Track if active state changed
        self.spinner_index = 0  # For loading animation
        self.spinner_chars = ["⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"]
        self._last_burn_rate = 0  # Track burn rate changes
        self._was_loading = True  # Track if we were showing loading screen
        
        # Detect if we're in IntelliJ or similar terminal with poor Unicode support
        self.is_intellij = os.environ.get('TERMINAL_EMULATOR') == 'JetBrains-JediTerm' or \
                          'IntelliJ' in os.environ.get('TERM_PROGRAM', '') or \
                          'idea' in os.environ.get('TERM', '').lower()
        
        # Initialize curses
        self.init_curses()
        
        # Window dimensions
        self.height, self.width = stdscr.getmaxyx()
        
        # Color pairs
        self.init_colors()
        
    def init_curses(self):
        """Initialize curses settings."""
        curses.curs_set(0)  # Hide cursor
        self.stdscr.nodelay(1)  # Non-blocking input
        self.stdscr.timeout(100)  # Refresh timeout
        self.stdscr.keypad(1)  # Enable keypad
        
        # Enable double buffering
        self.stdscr.idlok(True)
        self.stdscr.scrollok(False)
        
    def init_colors(self):
        """Initialize color pairs."""
        curses.start_color()
        curses.use_default_colors()
        
        # Define color pairs
        curses.init_pair(1, curses.COLOR_CYAN, -1)    # Cyan
        curses.init_pair(2, curses.COLOR_BLUE, -1)    # Blue
        curses.init_pair(3, curses.COLOR_RED, -1)     # Red
        curses.init_pair(4, curses.COLOR_YELLOW, -1)  # Yellow
        curses.init_pair(5, curses.COLOR_WHITE, -1)   # White
        curses.init_pair(6, curses.COLOR_GREEN, -1)   # Green
        curses.init_pair(7, curses.COLOR_MAGENTA, -1) # Magenta
        
        # Color attributes
        self.CYAN = curses.color_pair(1)
        self.BLUE = curses.color_pair(2)
        self.RED = curses.color_pair(3)
        self.YELLOW = curses.color_pair(4)
        self.WHITE = curses.color_pair(5) | curses.A_BOLD
        self.GREEN = curses.color_pair(6)
        self.MAGENTA = curses.color_pair(7)
        self.DIM = curses.A_DIM
        
    def run_ccusage(self):
        """Execute ccusage blocks --json command and return parsed JSON data."""
        try:
            result = subprocess.run(
                ["npx", "ccusage", "blocks", "--json"],
                capture_output=True,
                text=True,
                check=True,
            )
            return json.loads(result.stdout)
        except (subprocess.CalledProcessError, json.JSONDecodeError):
            return None
            
    def calculate_hourly_burn_rate(self, blocks, current_time):
        """Calculate burn rate based on all sessions in the last hour."""
        if not blocks:
            return 0

        one_hour_ago = current_time - timedelta(hours=1)
        total_tokens = 0

        for block in blocks:
            start_time_str = block.get("startTime")
            if not start_time_str:
                continue

            # Parse start time
            start_time = datetime.fromisoformat(start_time_str.replace("Z", "+00:00"))

            # Skip gaps
            if block.get("isGap", False):
                continue

            # Determine session end time
            if block.get("isActive", False):
                session_actual_end = current_time
            else:
                actual_end_str = block.get("actualEndTime")
                if actual_end_str:
                    session_actual_end = datetime.fromisoformat(
                        actual_end_str.replace("Z", "+00:00")
                    )
                else:
                    session_actual_end = current_time

            # Check if session overlaps with the last hour
            if session_actual_end < one_hour_ago:
                continue

            # Calculate how much of this session falls within the last hour
            session_start_in_hour = max(start_time, one_hour_ago)
            session_end_in_hour = min(session_actual_end, current_time)

            if session_end_in_hour <= session_start_in_hour:
                continue

            # Calculate portion of tokens used in the last hour
            total_session_duration = (
                session_actual_end - start_time
            ).total_seconds() / 60
            hour_duration = (
                session_end_in_hour - session_start_in_hour
            ).total_seconds() / 60

            if total_session_duration > 0:
                session_tokens = block.get("totalTokens", 0)
                tokens_in_hour = session_tokens * (hour_duration / total_session_duration)
                total_tokens += tokens_in_hour

        return total_tokens / 60 if total_tokens > 0 else 0
        
    def get_next_reset_time(self, current_time):
        """Calculate next token reset time."""
        try:
            target_tz = pytz.timezone(self.args.timezone)
        except pytz.exceptions.UnknownTimeZoneError:
            target_tz = pytz.timezone("Europe/Warsaw")

        if current_time.tzinfo is not None:
            target_time = current_time.astimezone(target_tz)
        else:
            target_time = target_tz.localize(current_time)

        if self.args.reset_hour is not None:
            reset_hours = [self.args.reset_hour]
        else:
            reset_hours = [4, 9, 14, 18, 23]

        current_hour = target_time.hour
        current_minute = target_time.minute

        next_reset_hour = None
        for hour in reset_hours:
            if current_hour < hour or (current_hour == hour and current_minute == 0):
                next_reset_hour = hour
                break

        if next_reset_hour is None:
            next_reset_hour = reset_hours[0]
            next_reset_date = target_time.date() + timedelta(days=1)
        else:
            next_reset_date = target_time.date()

        next_reset = target_tz.localize(
            datetime.combine(
                next_reset_date, datetime.min.time().replace(hour=next_reset_hour)
            ),
            is_dst=None,
        )

        if current_time.tzinfo is not None and current_time.tzinfo != target_tz:
            next_reset = next_reset.astimezone(current_time.tzinfo)

        return next_reset
        
    def get_token_limit(self, plan, blocks=None):
        """Get token limit based on plan type."""
        if plan == "custom_max" and blocks:
            max_tokens = 0
            for block in blocks:
                if not block.get("isGap", False) and not block.get("isActive", False):
                    tokens = block.get("totalTokens", 0)
                    if tokens > max_tokens:
                        max_tokens = tokens
            return max_tokens if max_tokens > 0 else 7000

        limits = {"pro": 7000, "max5": 35000, "max20": 140000}
        return limits.get(plan, 7000)
        
    def format_time(self, minutes):
        """Format minutes into human-readable time."""
        if minutes < 60:
            return f"{int(minutes)}m"
        hours = int(minutes // 60)
        mins = int(minutes % 60)
        if mins == 0:
            return f"{hours}h"
        return f"{hours}h {mins}m"
        
    def draw_header(self, y):
        """Draw the header."""
        if y >= self.height - 2:
            return y
            
        title = "CLAUDE CODE USAGE MONITOR"
        sparkles = "* * * *" if self.is_intellij else "✦ ✧ ✦ ✧"
        
        # Left-aligned header like in screenshot
        x = 2
        
        try:
            # Clear header lines
            self.stdscr.move(y, 0)
            self.stdscr.clrtoeol()
            
            self.stdscr.attron(self.CYAN | curses.A_BOLD)
            self.stdscr.addstr(y, x, f"{sparkles} {title} {sparkles}")
            self.stdscr.attroff(self.CYAN | curses.A_BOLD)
            
            # Draw separator line
            y += 1
            if y < self.height - 1:
                self.stdscr.move(y, 0)
                self.stdscr.clrtoeol()
                separator = "=" * min(70, self.width - 4)
                self.stdscr.attron(self.BLUE)
                self.stdscr.addstr(y, x, separator)
                self.stdscr.attroff(self.BLUE)
                
            # Add subtitle with plan info
            y += 1
            if y < self.height - 1:
                self.stdscr.move(y, 0)
                self.stdscr.clrtoeol()
                
                # Build subtitle
                plan_display = {
                    "pro": "Pro Plan",
                    "max5": "Max x5 Plan",
                    "max20": "Max x20 Plan",
                    "custom_max": f"Custom Max ({self.token_limit:,} tokens)"
                }
                plan_text = plan_display.get(self.args.plan, "Unknown Plan")
                subtitle = f"[ {plan_text} | {self.args.timezone} ]"
                
                # Left align subtitle
                subtitle_x = x
                    
                self.stdscr.attron(self.DIM)
                self.stdscr.addstr(y, subtitle_x, subtitle)
                self.stdscr.attroff(self.DIM)
                
        except curses.error:
            pass
        
        return y + 2  # Return next available line with spacing
        
    def draw_progress_bar(self, y, x, label, percentage, width, filled_color, empty_color, icon=""):
        """Draw a progress bar."""
        # Check bounds
        if y >= self.height - 1:
            return
            
        try:
            # Clear the line first to avoid artifacts
            self.stdscr.move(y, 0)
            self.stdscr.clrtoeol()
            
            # Draw icon first if provided (use ASCII for IntelliJ)
            if icon:
                if self.is_intellij:
                    ascii_icon = "[T]" if icon == "📊" else "[R]"
                    self.stdscr.addstr(y, x, ascii_icon + " ")
                    x += 4
                else:
                    self.stdscr.addstr(y, x, icon + " ")
                    x += 3
                
            # Label with bold
            self.stdscr.attron(self.WHITE | curses.A_BOLD)
            self.stdscr.addstr(y, x, label + ":")
            self.stdscr.attroff(self.WHITE | curses.A_BOLD)
            
            # Fixed label width for alignment
            label_width = 15
            current_x = x + len(label) + 1
            padding = label_width - len(label) - 1
            if padding > 0:
                self.stdscr.addstr(" " * padding)
                
            # Bar position - use absolute positioning for consistency
            bar_x = x + label_width + 1
                
            # Calculate bar width
            bar_width = min(width, self.width - bar_x - 10)
            if bar_width <= 0:
                return
                
            filled = int(bar_width * percentage / 100)
            
            # Progress indicator emoji  
            if icon == "📊":
                indicator = "[T]" if self.is_intellij else "🟢"
            else:
                indicator = "[R]" if self.is_intellij else "⏰"
            
            # Draw indicator and bar
            try:
                self.stdscr.move(y, bar_x)
                self.stdscr.addstr(indicator + " [")
            except curses.error:
                return
            
            # Filled part
            if filled > 0:
                self.stdscr.attron(filled_color | curses.A_BOLD)
                self.stdscr.addstr("█" * filled)
                self.stdscr.attroff(filled_color | curses.A_BOLD)
                
            # Empty part
            if bar_width - filled > 0:
                self.stdscr.attron(empty_color)
                self.stdscr.addstr("░" * (bar_width - filled))
                self.stdscr.attroff(empty_color)
                
            self.stdscr.addstr("] ")
            
            # Percentage with bold
            self.stdscr.attron(curses.A_BOLD)
            self.stdscr.addstr(f"{percentage:.1f}%")
            self.stdscr.attroff(curses.A_BOLD)
        except curses.error:
            pass
            
    def draw_stat_line(self, y, x, icon, label, value, suffix="", value_color=None):
        """Draw a statistics line."""
        # Check bounds
        if y >= self.height - 1:
            return
            
        try:
            # Clear the line first
            self.stdscr.move(y, 0)
            self.stdscr.clrtoeol()
            
            # Draw icon (use ASCII for IntelliJ)
            if self.is_intellij:
                ascii_icons = {
                    "🎯": "[o]",
                    "🔥": "[!]",
                    "🏁": "[F]",
                    "🔄": "[R]"
                }
                display_icon = ascii_icons.get(icon, "[?]")
            else:
                display_icon = icon
            self.stdscr.addstr(y, x, display_icon + " ")
            
            # Draw label with bold
            self.stdscr.attron(self.WHITE | curses.A_BOLD)
            self.stdscr.addstr(f"{label}:")
            self.stdscr.attroff(self.WHITE | curses.A_BOLD)
            
            # Add padding to align values
            icon_width = 4 if self.is_intellij else 2  # ASCII icons are wider
            current_pos = x + icon_width + len(label) + 1  # icon + space + label + colon
            target_pos = x + 17  # Align values at this position
            padding = target_pos - current_pos
            if padding > 0:
                self.stdscr.addstr(" " * padding)
                
            # Value
            if value_color:
                self.stdscr.attron(value_color)
            self.stdscr.addstr(str(value))
            if value_color:
                self.stdscr.attroff(value_color)
                
            # Suffix
            if suffix:
                self.stdscr.attron(self.DIM)
                self.stdscr.addstr(suffix)
                self.stdscr.attroff(self.DIM)
        except curses.error:
            # Ignore errors when writing at screen edge
            pass
            
    def get_velocity_indicator(self, burn_rate):
        """Get velocity emoji based on burn rate."""
        if burn_rate < 50:
            return "🐌"
        elif burn_rate < 150:
            return "➡️"
        elif burn_rate < 300:
            return "🚀"
        else:
            return "⚡"
            
    def update_data(self):
        """Update data in background thread."""
        while self.running:
            data = self.run_ccusage()
            if data:
                with self.data_lock:
                    # Check if data actually changed
                    if self.current_data != data:
                        self.current_data = data
                        self.data_changed = True
                    
                    # Update token limit for custom_max
                    if self.args.plan == "custom_max" and "blocks" in data:
                        new_limit = self.get_token_limit(self.args.plan, data["blocks"])
                        if new_limit != self.token_limit:
                            self.token_limit = new_limit
                            self.data_changed = True
                    elif self.token_limit == 7000:  # Only set once
                        self.token_limit = self.get_token_limit(self.args.plan)
                        self.data_changed = True
                        
            time.sleep(3.0)
            
    def draw_screen(self):
        """Draw the main screen."""
        # Only clear if dimensions changed
        new_height, new_width = self.stdscr.getmaxyx()
        if hasattr(self, '_last_height') and (self._last_height != new_height or self._last_width != new_width):
            self.stdscr.clear()
            self._screen_needs_full_redraw = True
        self._last_height = new_height
        self._last_width = new_width
        
        # Update dimensions
        self.height, self.width = new_height, new_width
        
        # Check minimum size
        if self.height < 14 or self.width < 80:
            try:
                self.stdscr.clear()
                msg = "Terminal too small!"
                min_msg = "Min: 80x14"
                current_msg = f"Current: {self.width}x{self.height}"
                
                if self.height >= 3:
                    self.stdscr.addstr(0, 0, msg)
                    if self.height >= 4:
                        self.stdscr.addstr(1, 0, min_msg)
                    if self.height >= 5:
                        self.stdscr.addstr(2, 0, current_msg)
            except curses.error:
                pass
            self.stdscr.refresh()
            return
        
        # Check if we're transitioning from loading to data
        with self.data_lock:
            transitioning = self._was_loading and self.current_data
            if transitioning:
                self._was_loading = False
                self._screen_needs_full_redraw = True
        
        # Only erase on first draw or when needed
        if not hasattr(self, '_first_draw_done') or getattr(self, '_screen_needs_full_redraw', False):
            self.stdscr.clear()  # Use clear instead of erase for complete clearing
            self._first_draw_done = True
            self._screen_needs_full_redraw = False
        
        # Always draw header first
        y = 0
        y = self.draw_header(y)
        
        # Check if we have data
        with self.data_lock:
            if not self.current_data:
                # Show loading message with spinner
                y += 1  # Add spacing after header
                self.stdscr.attron(self.YELLOW | curses.A_BOLD)
                spinner = self.spinner_chars[self.spinner_index % len(self.spinner_chars)]
                self.stdscr.addstr(y, 2, f"{spinner} Initializing Claude Code Usage Monitor...")
                self.stdscr.attroff(self.YELLOW | curses.A_BOLD)
                
                y += 2
                self.stdscr.attron(self.DIM)
                self.stdscr.addstr(y, 2, "⏳ Fetching usage data from ccusage...")
                y += 1
                self.stdscr.addstr(y, 2, "⚡ This may take a moment on first run")
                self.stdscr.attroff(self.DIM)
                
                self.spinner_index += 1
                self.stdscr.refresh()
                return
                
            if "blocks" not in self.current_data:
                self.stdscr.attron(self.RED | curses.A_BOLD)
                self.stdscr.addstr(y, 2, "❌ Failed to get usage data")
                self.stdscr.attroff(self.RED | curses.A_BOLD)
                self.stdscr.refresh()
                return
                
            # Find active block
            active_block = None
            for block in self.current_data["blocks"]:
                if block.get("isActive", False):
                    active_block = block
                    break
            
            # Check if active state changed
            current_active_state = active_block is not None
            if self._last_active_state != current_active_state:
                self._screen_needs_full_redraw = True  # Mark for full redraw instead of immediate clear
                self._last_active_state = current_active_state
                    
            if not active_block:
                # Clear any remaining loading text
                for i in range(3):
                    if y + i < self.height:
                        self.stdscr.move(y + i, 0)
                        self.stdscr.clrtoeol()
                
                # No active session
                self.draw_progress_bar(y, 2, "Token Usage", 0.0, 60, self.GREEN, self.RED, "📊")
                y += 2
                
                self.draw_progress_bar(y, 2, "Time to Reset", 0.0, 60, self.BLUE, self.RED, "⏳")
                y += 2
                
                self.draw_stat_line(y, 2, "🎯", "Tokens", "0", f" / ~{self.token_limit:,} (0 left)", self.WHITE)
                y += 1
                
                self.draw_stat_line(y, 2, "🔥", "Burn Rate", "0.0", " tokens/min", self.YELLOW)
                y += 2
                
                # Status line
                if y < self.height - 1:
                    try:
                        time_str = datetime.now().strftime('%H:%M:%S')
                        if self.is_intellij:
                            self.stdscr.addstr(y, 2, f"[{time_str}] ")
                        else:
                            self.stdscr.addstr(y, 2, f"⏰ {time_str} ")
                            self.stdscr.addstr("🐌 ")
                        
                        self.stdscr.attron(self.CYAN | curses.A_BOLD)
                        self.stdscr.addstr("No active session")
                        self.stdscr.attroff(self.CYAN | curses.A_BOLD)
                        
                        self.stdscr.addstr("  |  ")
                        
                        self.stdscr.addstr("Ctrl+C to exit")
                        
                        if not self.is_intellij:
                            self.stdscr.addstr("  🟨")
                    except curses.error:
                        pass
                
                self.stdscr.refresh()
                return
                
            # Clear any remaining loading text
            for i in range(3):
                if y + i < self.height:
                    self.stdscr.move(y + i, 0)
                    self.stdscr.clrtoeol()
            
            # Extract data from active block
            tokens_used = active_block.get("totalTokens", 0)
            
            # Check if tokens exceed limit and switch to custom_max if needed
            if tokens_used > self.token_limit and self.args.plan == "pro":
                new_limit = self.get_token_limit("custom_max", self.current_data["blocks"])
                if new_limit > self.token_limit:
                    self.token_limit = new_limit
                    
            usage_percentage = (tokens_used / self.token_limit) * 100 if self.token_limit > 0 else 0
            tokens_left = self.token_limit - tokens_used
            
            # Time calculations
            start_time_str = active_block.get("startTime")
            if start_time_str:
                start_time = datetime.fromisoformat(start_time_str.replace("Z", "+00:00"))
                current_time = datetime.now(start_time.tzinfo)
            else:
                current_time = datetime.now()
                
            # Calculate burn rate
            burn_rate = self.calculate_hourly_burn_rate(self.current_data["blocks"], current_time)
            
            # Reset time calculation
            reset_time = self.get_next_reset_time(current_time)
            time_to_reset = reset_time - current_time
            minutes_to_reset = time_to_reset.total_seconds() / 60
            
            # Predicted end calculation
            if burn_rate > 0 and tokens_left > 0:
                minutes_to_depletion = tokens_left / burn_rate
                predicted_end_time = current_time + timedelta(minutes=minutes_to_depletion)
            else:
                predicted_end_time = reset_time
                
            # Draw Token Usage
            self.draw_progress_bar(y, 2, "Token Usage", usage_percentage, 60, self.GREEN, self.RED, "📊")
            y += 2
            
            # Draw Time to Reset
            time_since_reset = max(0, 300 - minutes_to_reset)
            time_percentage = (time_since_reset / 300) * 100 if 300 > 0 else 0
            self.draw_progress_bar(y, 2, "Time to Reset", time_percentage, 60, self.BLUE, self.RED, "⏳")
            
            # Add remaining time on the same line
            remaining_time = self.format_time(minutes_to_reset)
            try:
                # Add some spacing and the remaining time
                self.stdscr.addstr("  ")
                self.stdscr.attron(curses.A_BOLD)
                self.stdscr.addstr(remaining_time)
                self.stdscr.attroff(curses.A_BOLD)
            except curses.error:
                pass
            y += 2
            
            # Token stats - custom formatting to match screenshot
            try:
                # Icon and label
                self.stdscr.addstr(y, 2, "🎯 ")
                self.stdscr.attron(self.WHITE | curses.A_BOLD)
                self.stdscr.addstr("Tokens:")
                self.stdscr.attroff(self.WHITE | curses.A_BOLD)
                
                # Padding for alignment
                self.stdscr.addstr(" " * 8)
                
                # Tokens used (normal, not bold)
                self.stdscr.addstr(f"{tokens_used:,}")
                
                # Separator
                self.stdscr.attron(self.DIM)
                self.stdscr.addstr(" / ~")
                self.stdscr.attroff(self.DIM)
                
                # Token limit (normal)
                self.stdscr.addstr(f"{self.token_limit:,}")
                
                # Tokens left (cyan)
                self.stdscr.addstr(" (")
                if tokens_left > 0:
                    self.stdscr.attron(self.CYAN)
                else:
                    self.stdscr.attron(self.RED)
                self.stdscr.addstr(f"{tokens_left:,} left")
                if tokens_left > 0:
                    self.stdscr.attroff(self.CYAN)
                else:
                    self.stdscr.attroff(self.RED)
                self.stdscr.addstr(")")
            except curses.error:
                pass
            y += 1
            
            # Burn rate with color based on value
            burn_color = self.GREEN if burn_rate < 50 else self.YELLOW if burn_rate < 150 else self.RED
            self.draw_stat_line(y, 2, "🔥", "Burn Rate", f"{burn_rate:.1f}", " tokens/min", burn_color)
            y += 2
            
            # Predictions
            try:
                local_tz = pytz.timezone(self.args.timezone)
            except pytz.exceptions.UnknownTimeZoneError:
                local_tz = pytz.timezone("Europe/Warsaw")
                
            predicted_end_local = predicted_end_time.astimezone(local_tz)
            reset_time_local = reset_time.astimezone(local_tz)
            
            self.draw_stat_line(y, 2, "🏁", "Predicted End", predicted_end_local.strftime("%H:%M"))
            y += 1
            
            self.draw_stat_line(y, 2, "🔄", "Token Reset", reset_time_local.strftime("%H:%M"))
            y += 2
            
            # Notifications
            if tokens_used > 7000 and self.args.plan == "pro" and self.token_limit > 7000:
                self.stdscr.attron(self.CYAN)
                if self.is_intellij:
                    self.stdscr.addstr(y, 2, f"[S] Tokens exceeded Pro limit - switched to custom_max ({self.token_limit:,})")
                else:
                    self.stdscr.addstr(y, 2, f"🔄 Tokens exceeded Pro limit - switched to custom_max ({self.token_limit:,})")
                self.stdscr.attroff(self.CYAN)
                y += 2
                
            if tokens_used > self.token_limit:
                self.stdscr.attron(self.RED | curses.A_BOLD | curses.A_BLINK)
                self.stdscr.addstr(y, 2, f"🚨 TOKENS EXCEEDED MAX LIMIT! ({tokens_used:,} > {self.token_limit:,})")
                self.stdscr.attroff(self.RED | curses.A_BOLD | curses.A_BLINK)
                y += 2
                
            if predicted_end_time < reset_time and burn_rate > 0:
                self.stdscr.attron(self.RED | curses.A_BOLD)
                self.stdscr.addstr(y, 2, "⚠️  Tokens will run out BEFORE reset!")
                self.stdscr.attroff(self.RED | curses.A_BOLD)
                y += 2
                
            # Status line
            if y < self.height - 1:
                try:
                    velocity = self.get_velocity_indicator(burn_rate)
                    
                    # Time
                    time_str = datetime.now().strftime('%H:%M:%S')
                    if self.is_intellij:
                        self.stdscr.addstr(y, 2, f"[{time_str}] ")
                    else:
                        self.stdscr.addstr(y, 2, "⏰ ")
                        self.stdscr.addstr(time_str)
                        self.stdscr.addstr(" ")
                    
                    # Velocity indicator
                    if not self.is_intellij:
                        self.stdscr.addstr(f"{velocity} ")
                    
                    # Status message
                    if burn_rate > 300:
                        self.stdscr.attron(self.RED | curses.A_BOLD)
                        self.stdscr.addstr("Burning fast!")
                    elif burn_rate > 150:
                        self.stdscr.attron(self.YELLOW | curses.A_BOLD)
                        self.stdscr.addstr("High usage")
                    else:
                        self.stdscr.attron(self.CYAN | curses.A_BOLD)
                        self.stdscr.addstr("Smooth sailing...")
                    self.stdscr.attroff(self.CYAN | self.YELLOW | self.RED | curses.A_BOLD)
                    
                    self.stdscr.addstr("  |  ")
                    
                    self.stdscr.addstr("Ctrl+C to exit")
                    
                    if not self.is_intellij:
                        self.stdscr.addstr("  🟨")
                except curses.error:
                    pass
            
            
        self.stdscr.refresh()
        
    def run(self):
        """Main run loop."""
        # Start data update thread
        update_thread = threading.Thread(target=self.update_data, daemon=True)
        update_thread.start()
        
        # Force initial draw with loading message
        self.draw_screen()
        
        # Initial data fetch
        data = self.run_ccusage()
        if data:
            with self.data_lock:
                self.current_data = data
                self.data_changed = True  # Mark data as changed to trigger screen update
                if self.args.plan == "custom_max" and "blocks" in data:
                    self.token_limit = self.get_token_limit(self.args.plan, data["blocks"])
                else:
                    self.token_limit = self.get_token_limit(self.args.plan)
        
        try:
            while True:
                # Check for quit key
                key = self.stdscr.getch()
                if key == ord('q') or key == ord('Q'):
                    break
                    
                # Only draw screen if data changed or enough time passed
                current_time = time.time()
                if self.data_changed or (current_time - self.last_update_time) >= self.screen_update_interval:
                    with self.data_lock:
                        self.data_changed = False
                    
                    self.draw_screen()
                    self.last_update_time = current_time
                
                # Small delay to prevent CPU spinning
                time.sleep(0.05)  # Reduced from 0.1 to be more responsive
                
        except KeyboardInterrupt:
            pass
        finally:
            self.running = False
            

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Claude Code Usage Monitor - Real-time token usage monitoring"
    )
    parser.add_argument(
        "--plan",
        type=str,
        default="pro",
        choices=["pro", "max5", "max20", "custom_max"],
        help='Claude plan type (default: pro). Use "custom_max" to auto-detect from highest previous block',
    )
    parser.add_argument(
        "--reset-hour", type=int, help="Change the reset hour (0-23) for daily limits"
    )
    parser.add_argument(
        "--timezone",
        type=str,
        default="Europe/Warsaw",
        help="Timezone for reset times (default: Europe/Warsaw). Examples: US/Eastern, Asia/Tokyo, UTC",
    )
    return parser.parse_args()

def main(stdscr=None):
    # bootstrap under curses.wrapper if no stdscr was passed in
    if stdscr is None:
        curses.wrapper(main)
        return

    # … now stdscr is a real curses window, so do your work …
    args = parse_args()
    monitor = TokenMonitor(stdscr, args)
    monitor.run()

if __name__ == "__main__":
    # only for direct `python claude_monitor.py` runs
    test_node()
    test_npx()
    curses.wrapper(main)
