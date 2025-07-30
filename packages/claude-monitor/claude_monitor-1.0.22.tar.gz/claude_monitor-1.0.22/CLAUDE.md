# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Claude Code Usage Monitor is a real-time terminal monitoring tool for tracking Claude AI token usage. It displays token consumption, burn rate calculations, and predictions about when tokens will run out.

## Development Commands

### Setup and Installation
```bash
# Install with development dependencies (recommended)
uv sync --extra dev

# Alternative: pip install
pip install -e ".[dev]"
```

### Linting and Formatting
```bash
# Run linter
ruff check .

# Run formatter
ruff format .

# Auto-fix linting issues
ruff check --fix .

# Check formatting without changes
ruff format --check .
```

### Pre-commit Hooks
```bash
# Install pre-commit
uv tool install pre-commit --with pre-commit-uv

# Install hooks
pre-commit install

# Run on all files
pre-commit run --all-files
```

## Architecture

The codebase follows a modular architecture with two main packages:

### claude_monitor/
Main package containing:
- `monitoring/`: Core monitoring logic including Monitor class, SessionManager, and TokenTracker
- `terminal/`: Terminal UI components with Display class for rendering
- `utils/`: Utility functions for data processing and time calculations
- Entry point: `claude_monitor.main()`

### usage_analyzer/
Separate API for analyzing usage data:
- `core/`: Core analysis logic
- `models/`: Data models for usage patterns
- `output/`: Output formatting utilities
- `api.py`: Main API entry point

## Key Development Notes

1. **Data Source**: Monitors Claude's local usage data from `~/.claude/usage.jsonl`
2. **Refresh Rate**: UI updates every 3 seconds
3. **Token Plans**: Supports Pro, Max5, Max20, and custom_max plans
4. **No Tests Yet**: Testing infrastructure is not implemented - consider adding pytest when creating new features
5. **Active Branch**: Current development on `improve-analyze-jsonl`

## Common Development Tasks

### Adding New Features
1. Follow existing module structure (monitoring/, terminal/, utils/)
2. Use type hints throughout
3. Maintain separation between data logic and UI rendering
4. Run linting before committing: `ruff check . && ruff format .`

### Working with Usage Data
- Session data comes from `~/.claude/usage.jsonl`
- TokenTracker handles all token calculations
- Display class manages all terminal rendering
- Use rich library for UI components

### Making UI Changes
- All UI logic is in `terminal/display.py`
- Use rich.console for rendering
- Maintain 3-second refresh cycle
- Keep UI responsive during data processing