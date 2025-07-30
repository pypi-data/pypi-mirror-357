"""Claude Monitor - Real-time token usage monitoring for Claude."""

__version__ = "1.0.0"
__author__ = "Claude Monitor Team"

from .config import Config
from .main import main

__all__ = ["Config", "main", "__version__"]
