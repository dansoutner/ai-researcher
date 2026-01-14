"""Logging utilities for agent_v3_claude with colored output.

This module provides a structured logging system with color-coded output to distinguish
between different types of messages:
- DEBUG: Cyan - internal system operations
- INFO: Green - important state changes and progress
- WARNING: Yellow - potential issues
- ERROR: Red - errors and failures
- USER: Magenta - messages intended for end users (results, summaries)
- TOOL: Blue - tool execution details
"""

import logging
import sys


# ANSI color codes
class Colors:
    """ANSI color codes for terminal output."""
    RESET = "\033[0m"
    BOLD = "\033[1m"

    # Regular colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # Bright colors
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"


# Custom log level for user-facing messages
USER_LEVEL = 25  # Between INFO (20) and WARNING (30)
TOOL_LEVEL = 15  # Between DEBUG (10) and INFO (20)

logging.addLevelName(USER_LEVEL, "USER")
logging.addLevelName(TOOL_LEVEL, "TOOL")


class ColoredFormatter(logging.Formatter):
    """Custom formatter that adds colors based on log level."""

    LEVEL_COLORS = {
        logging.DEBUG: Colors.CYAN,
        TOOL_LEVEL: Colors.BLUE,
        logging.INFO: Colors.GREEN,
        USER_LEVEL: Colors.MAGENTA,
        logging.WARNING: Colors.YELLOW,
        logging.ERROR: Colors.RED,
        logging.CRITICAL: Colors.BOLD + Colors.RED,
    }

    def format(self, record):
        """Format log record with color."""
        # Add color to the level name
        levelname = record.levelname
        if record.levelno in self.LEVEL_COLORS:
            colored_levelname = (
                f"{self.LEVEL_COLORS[record.levelno]}"
                f"{levelname:5s}"
                f"{Colors.RESET}"
            )
            record.levelname = colored_levelname

        return super().format(record)


def setup_logger(
    name: str,
    level: int = logging.INFO,
    use_colors: bool = True,
) -> logging.Logger:
    """Set up a logger with colored output.

    Args:
        name: Logger name (typically __name__)
        level: Logging level (default: INFO)
        use_colors: Whether to use colored output (default: True)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Set the level
    logger.setLevel(level)

    # Add handler if not already present
    if not logger.handlers:
        # Create console handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)

        # Create formatter
        if use_colors and sys.stdout.isatty():
            formatter = ColoredFormatter(
                fmt="%(levelname)s | %(message)s",
                datefmt="%H:%M:%S"
            )
        else:
            formatter = logging.Formatter(
                fmt="%(levelname)s | %(message)s",
                datefmt="%H:%M:%S"
            )

        handler.setFormatter(formatter)
        logger.addHandler(handler)

    # Add custom logging methods if not already present
    if not hasattr(logger, 'user'):
        def user(self, message, *args, **kwargs):
            """Log a user-facing message."""
            if self.isEnabledFor(USER_LEVEL):
                self._log(USER_LEVEL, message, args, **kwargs)

        def tool(self, message, *args, **kwargs):
            """Log a tool execution detail."""
            if self.isEnabledFor(TOOL_LEVEL):
                self._log(TOOL_LEVEL, message, args, **kwargs)

        # Bind custom methods
        logger.user = user.__get__(logger, logging.Logger)
        logger.tool = tool.__get__(logger, logging.Logger)

    return logger


def get_logger(name: str, level: int = logging.DEBUG) -> logging.Logger:
    """Get or create a logger for the given name.

    Args:
        name: Logger name (typically __name__)
        level: Logging level (default: DEBUG)

    Returns:
        Logger instance with custom methods
    """
    logger = logging.getLogger(name)

    # If logger doesn't have custom methods, set it up
    if not hasattr(logger, 'user'):
        return setup_logger(name, level=level)

    return logger


# Default logger for the agent system
agent_logger = setup_logger("agent_v3_claude", level=logging.DEBUG)


def format_section_header(title: str, width: int = 60) -> str:
    """Format a section header for output.

    Args:
        title: Section title
        width: Total width of the header line

    Returns:
        Formatted header string
    """
    return "\n" + "=" * width + f"\n{title}\n" + "=" * width


def format_subsection_header(title: str, width: int = 60) -> str:
    """Format a subsection header for output.

    Args:
        title: Subsection title
        width: Total width of the header line

    Returns:
        Formatted header string
    """
    return "\n" + "-" * width + f"\n{title}\n" + "-" * width

