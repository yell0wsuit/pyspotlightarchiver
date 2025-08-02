"""Countdown utility for inline display."""

import time
from rich.console import Console

console = Console()


def inline_countdown(delay):
    """Display a countdown in the same line."""
    if delay <= 0:
        return
    for remaining in range(delay, 0, -1):
        mins, secs = divmod(remaining, 60)
        timeformat = f"ℹ️ [bisque]Delaying to avoid rate limiting... {mins}:{secs:02d} remaining[/bisque]"
        console.print(timeformat, end="\r", highlight=False, soft_wrap=True)
        time.sleep(1)
    # Clear the line after countdown
    console.print(" " * 60, end="\r")
