"""Utility helpers for the Twitter posting app.

Includes:
- get_api(): create a Tweepy API client using twitter_credentials.load_credentials
- compute_delay_seconds(): convert minutes or HH:MM time to a delay in seconds
- read_tweets_from_file(): read tweets line-by-line from .txt or .csv, ignoring blanks
"""

from __future__ import annotations

import csv
import os
import calendar
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

import tweepy

from twitter_credentials import load_credentials


def get_api() -> tweepy.API:
    """Create and return an authenticated Tweepy API client.

    Uses OAuth 1.0a user context with wait_on_rate_limit enabled.
    """
    api_key, api_secret, access_token, access_token_secret = load_credentials()
    auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_token_secret)
    return tweepy.API(auth, wait_on_rate_limit=True)


def compute_delay_seconds(
    *, delay_minutes: Optional[int] = None, time_hhmm: Optional[str] = None
) -> Tuple[float, str]:
    """Compute delay in seconds from either minutes or a clock time.

    Exactly one of delay_minutes or time_hhmm must be provided.

    Returns a tuple (seconds, scheduled_for_str) where scheduled_for_str is
    a human-friendly HH:MM 24h string of when it will run.
    """
    if (delay_minutes is None and not time_hhmm) or (
        delay_minutes is not None and time_hhmm
    ):
        raise ValueError("Provide either delay_minutes OR time_hhmm (HH:MM), not both.")

    now = datetime.now()
    if delay_minutes is not None:
        if delay_minutes < 0:
            raise ValueError("delay_minutes must be >= 0")
        run_time = now + timedelta(minutes=delay_minutes)
        seconds = max(0, (run_time - now).total_seconds())
        return seconds, run_time.strftime("%H:%M")

    # time_hhmm path
    try:
        hour, minute = map(int, time_hhmm.split(":", 1))
    except Exception as e:
        raise ValueError("time_hhmm must be in HH:MM 24h format") from e
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        raise ValueError("time_hhmm must be a valid 24h time")

    run_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if run_time <= now:
        run_time += timedelta(days=1)
    seconds = (run_time - now).total_seconds()
    return seconds, run_time.strftime("%H:%M")


def read_tweets_from_file(file_path: str) -> List[str]:
    """Read tweets from a .txt or .csv file, ignoring blank/whitespace-only lines.

    - .txt: each non-empty line is a tweet
    - .csv: first column per row is treated as the tweet text
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    _, ext = os.path.splitext(file_path.lower())
    tweets: List[str] = []

    if ext == ".csv":
        with open(file_path, "r", encoding="utf-8", newline="") as f:
            reader = csv.reader(f)
            for row in reader:
                if not row:
                    continue
                text = (row[0] or "").strip()
                if text:
                    tweets.append(text)
    else:
        # default to txt-like behavior
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                text = line.strip()
                if text:
                    tweets.append(text)

    return tweets


__all__ = ["get_api", "compute_delay_seconds", "read_tweets_from_file"]
 
 
def compute_delay_to_month_day_time(year: int, month: int, day: int, time_hhmm: str) -> tuple[float, str]:
    """Compute delay in seconds until a specific day and HH:MM in a given month/year.

    Only future times within the specified month are permitted.

    Returns: (seconds, when_str) where when_str is 'YYYY-MM-DD HH:MM'.
    """
    if day < 1 or day > calendar.monthrange(year, month)[1]:
        raise ValueError("Invalid day for this month")

    try:
        hour, minute = map(int, time_hhmm.split(":", 1))
    except Exception as e:
        raise ValueError("time_hhmm must be in HH:MM 24h format") from e
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        raise ValueError("time_hhmm must be a valid 24h time")

    now = datetime.now()
    run_time = datetime(year, month, day, hour, minute)
    if run_time <= now:
        raise ValueError("Selected date/time must be in the future within this month")

    seconds = (run_time - now).total_seconds()
    return seconds, run_time.strftime("%Y-%m-%d %H:%M")


__all__.append("compute_delay_to_month_day_time")
