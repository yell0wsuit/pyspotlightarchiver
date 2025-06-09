"""Countdown utility for inline display."""

import time


def inline_countdown(delay):
    """Display a countdown in the same line."""
    if delay <= 0:
        return
    timeformat = ""
    for remaining in range(delay, 0, -1):
        mins, secs = divmod(remaining, 60)
        timeformat = f"Delaying to avoid rate limiting... {mins}:{secs:02d} remaining"
        print(f"\r{timeformat}", end="", flush=True)
        time.sleep(1)
    print("\r" + " " * len(timeformat) + "\r", end="", flush=True)
