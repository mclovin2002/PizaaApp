"""
Post a tweet using Tweepy and X (Twitter) API credentials.

Where to get credentials:
- Create a developer account at https://developer.x.com/
- Create a Project + App in the Developer Portal
- Generate API Key, API Secret, Access Token, and Access Token Secret
- Ensure the app has write permissions to post tweets

Fill in the credentials below, then run:
    python tweet.py "Your tweet message here"
If no message is provided as an argument, the script will prompt for one.
"""

from __future__ import annotations

import sys
import threading
import time
from datetime import datetime, timedelta
import calendar
from typing import Optional

import tweepy
from twitter_credentials import load_credentials
from twitter_utils import (
    get_api,
    compute_delay_seconds,
    read_tweets_from_file,
    compute_delay_to_month_day_time,
)
from token_manager import get_tokens, consume_tokens
from ai_reply import build_reply_prompt, generate_reply_via_api


def _credentials_are_valid() -> bool:
    try:
        load_credentials()
        return True
    except Exception:
        return False


def post_tweet(message: str) -> None:
    """Authenticate with OAuth 1.0a and post a tweet.

    Raises:
        tweepy.TweepyException: When the API call fails.
        ValueError: If message is empty.
    """
    if not message or not message.strip():
        raise ValueError("Tweet message cannot be empty.")

    # OAuth 1.0a user context (API key/secret + access token/secret)
    api_key, api_secret, access_token, access_token_secret = load_credentials()

    auth = tweepy.OAuth1UserHandler(
        api_key,
        api_secret,
        access_token,
        access_token_secret,
    )

    # wait_on_rate_limit is harmless here but useful in general
    api = tweepy.API(auth, wait_on_rate_limit=True)

    # Optional: verify credentials to catch auth errors early
    api.verify_credentials()

    # Post the tweet using v1.1 endpoint
    api.update_status(status=message)


# === New features ===

def schedule_tweet(message: str, *, delay_minutes: Optional[int] = None, time_hhmm: Optional[str] = None) -> threading.Timer:
    """Schedule a tweet to be posted after a delay or at a specific HH:MM time.

    Returns the Timer instance. The caller may .cancel() it if needed.
    Prints both the schedule time and a confirmation once posted.
    """
    seconds, scheduled_for = compute_delay_seconds(delay_minutes=delay_minutes, time_hhmm=time_hhmm)

    def _send():
        try:
            post_tweet(message)
            print("Tweet sent successfully!")
        except tweepy.Unauthorized as e:
            print(f"Authentication failed (Unauthorized): {e}", file=sys.stderr)
        except tweepy.Forbidden as e:
            print(f"Permission error (Forbidden): {e}", file=sys.stderr)
        except tweepy.TooManyRequests as e:
            print(f"Rate limit exceeded: {e}", file=sys.stderr)
        except tweepy.TweepyException as e:
            print(f"Twitter API error: {e}", file=sys.stderr)
        except Exception as e:
            print(f"Unexpected error: {e}", file=sys.stderr)

    print(f"Tweet scheduled for {scheduled_for}...")
    timer = threading.Timer(seconds, _send)
    timer.daemon = True
    timer.start()
    return timer


def schedule_tweet_in_month(message: str, year: int, month: int, day: int, time_hhmm: str) -> threading.Timer:
    """Schedule a tweet for a specific day and time within a given month/year."""
    seconds, when_str = compute_delay_to_month_day_time(year, month, day, time_hhmm)

    def _send():
        try:
            post_tweet(message)
            print("Tweet sent successfully!")
        except tweepy.Unauthorized as e:
            print(f"Authentication failed (Unauthorized): {e}", file=sys.stderr)
        except tweepy.Forbidden as e:
            print(f"Permission error (Forbidden): {e}", file=sys.stderr)
        except tweepy.TooManyRequests as e:
            print(f"Rate limit exceeded: {e}", file=sys.stderr)
        except tweepy.TweepyException as e:
            print(f"Twitter API error: {e}", file=sys.stderr)
        except Exception as e:
            print(f"Unexpected error: {e}", file=sys.stderr)

    print(f"Tweet scheduled for {when_str}...")
    timer = threading.Timer(seconds, _send)
    timer.daemon = True
    timer.start()
    return timer


def bulk_post_from_file(file_path: str, delay_minutes: int) -> None:
    """Read tweets from file and post them sequentially with a delay between each.

    Logs success/failure per tweet. delay_minutes can be 0.
    """
    tweets = read_tweets_from_file(file_path)
    if not tweets:
        print("No tweets found in file.")
        return

    delay_seconds = max(0, int(delay_minutes)) * 60
    for idx, t in enumerate(tweets, start=1):
        try:
            post_tweet(t)
            print(f"[{idx}/{len(tweets)}] Sent: {t!r}")
        except tweepy.Unauthorized as e:
            print(f"[{idx}] Unauthorized: {e}", file=sys.stderr)
        except tweepy.Forbidden as e:
            print(f"[{idx}] Forbidden: {e}", file=sys.stderr)
        except tweepy.TooManyRequests as e:
            print(f"[{idx}] Rate limited: {e}", file=sys.stderr)
        except tweepy.TweepyException as e:
            print(f"[{idx}] API error: {e}", file=sys.stderr)
        except Exception as e:
            print(f"[{idx}] Unexpected error: {e}", file=sys.stderr)

        if idx < len(tweets) and delay_seconds:
            time.sleep(delay_seconds)


def bulk_schedule_from_file(file_path: str, frequency_minutes: int) -> list[threading.Timer]:
    """Schedule tweets from file at the given frequency (minutes) between posts.

    Returns list of Timer objects for possible cancellation.
    """
    tweets = read_tweets_from_file(file_path)
    if not tweets:
        print("No tweets found in file.")
        return []

    timers: list[threading.Timer] = []
    for i, tmsg in enumerate(tweets):
        seconds = max(0, i * frequency_minutes * 60)

        def make_send(message):
            def _send():
                try:
                    post_tweet(message)
                    print("Tweet sent successfully!")
                except Exception as e:
                    print(f"Scheduled bulk post failed: {e}", file=sys.stderr)

            return _send

        when = datetime.now() + timedelta(seconds=seconds)
        print(f"Tweet scheduled for {when.strftime('%Y-%m-%d %H:%M')}...")
        timer = threading.Timer(seconds, make_send(tmsg))
        timer.daemon = True
        timer.start()
        timers.append(timer)

    return timers


def auto_reply_ai(interval_minutes: int, user_spec: str, frequency_limit_tokens: int = 500) -> None:
    """Auto-reply using AI: periodically fetch mentions, generate replies via AI, and post.

    Each reply consumes 1 token from token_manager. The function runs until interrupted.
    """
    api = get_api()

    def load_last_id(state_file: str = "last_mention_id_ai.txt") -> Optional[int]:
        try:
            with open(state_file, "r", encoding="utf-8") as f:
                s = f.read().strip()
                return int(s) if s else None
        except FileNotFoundError:
            return None
        except Exception:
            return None

    def save_last_id(tweet_id: int, state_file: str = "last_mention_id_ai.txt") -> None:
        try:
            with open(state_file, "w", encoding="utf-8") as f:
                f.write(str(tweet_id))
        except Exception as e:
            print(f"Warning: failed to write state file: {e}", file=sys.stderr)

    last_id = load_last_id()
    delay = max(1, int(interval_minutes)) * 60
    print("AI Auto-reply mode enabled. Press Ctrl+C to stop.")
    while True:
        try:
            mentions = api.mentions_timeline(since_id=last_id, tweet_mode="extended")
            for m in reversed(mentions):
                screen_name = getattr(m.user, "screen_name", None)
                text = getattr(m, "full_text", None) or getattr(m, "text", "")
                if not screen_name:
                    continue

                # Check tokens
                left, limit = get_tokens()
                if left <= 0:
                    print("Token limit reached for this month. Stopping AI replies.")
                    return

                prompt = build_reply_prompt(user_spec, text)
                reply_text = generate_reply_via_api(prompt)

                # Consume token
                ok = consume_tokens(1)
                if not ok:
                    print("Failed to consume token; stopping AI replies")
                    return

                try:
                    to_post = f"@{screen_name} {reply_text}"
                    api.update_status(status=to_post, in_reply_to_status_id=m.id)
                    print(f"Replied to @{screen_name} (id={m.id}) via AI")
                    last_id = m.id
                    save_last_id(last_id)
                except Exception as e:
                    print(f"Failed to post AI reply: {e}", file=sys.stderr)
        except KeyboardInterrupt:
            print("\nAI Auto-reply stopped by user.")
            break
        except Exception as e:
            print(f"Unexpected error: {e}", file=sys.stderr)

        time.sleep(delay)


def auto_reply_to_mentions(interval_minutes: int, reply_message: str, state_file: str = "last_mention_id.txt") -> None:
    """Periodically check mentions and reply to new ones with reply_message.

    Keeps last replied mention ID in a local file to avoid duplicates.
    Runs until interrupted (Ctrl+C).
    """
    api = get_api()

    def load_last_id() -> Optional[int]:
        try:
            with open(state_file, "r", encoding="utf-8") as f:
                s = f.read().strip()
                return int(s) if s else None
        except FileNotFoundError:
            return None
        except Exception:
            return None

    def save_last_id(tweet_id: int) -> None:
        try:
            with open(state_file, "w", encoding="utf-8") as f:
                f.write(str(tweet_id))
        except Exception as e:
            print(f"Warning: failed to write state file: {e}", file=sys.stderr)

    last_id = load_last_id()
    delay = max(1, int(interval_minutes)) * 60
    print("Auto-reply mode enabled. Press Ctrl+C to stop.")
    while True:
        try:
            mentions = api.mentions_timeline(since_id=last_id, tweet_mode="extended")
            # mentions are returned newest first; process oldest-to-newest
            for m in reversed(mentions):
                screen_name = getattr(m.user, "screen_name", None)
                if not screen_name:
                    continue
                reply_text = f"@{screen_name} {reply_message}"
                api.update_status(status=reply_text, in_reply_to_status_id=m.id)
                print(f"Replied to @{screen_name} (id={m.id})")
                last_id = m.id
                save_last_id(last_id)
        except tweepy.Unauthorized as e:
            print(f"Authentication failed (Unauthorized): {e}", file=sys.stderr)
        except tweepy.Forbidden as e:
            print(f"Permission error (Forbidden): {e}", file=sys.stderr)
        except tweepy.TooManyRequests as e:
            print(f"Rate limit exceeded: {e}", file=sys.stderr)
        except tweepy.TweepyException as e:
            print(f"Twitter API error: {e}", file=sys.stderr)
        except KeyboardInterrupt:
            print("\nAuto-reply stopped by user.")
            break
        except Exception as e:
            print(f"Unexpected error: {e}", file=sys.stderr)

        time.sleep(delay)


def _interactive_menu() -> None:
    """Simple interactive menu for running common tasks."""
    print("\nTwitter Posting App")
    print("[1] Post a tweet now")
    print("[2] Schedule a tweet (minutes/HH:MM)")
    print("[3] Schedule a tweet within this month (pick day + time)")
    print("[4] Bulk post from file")
    print("[5] Bulk scheduler (file + frequency minutes)")
    print("[6] Enable auto-reply mode")
    print("[7] Exit")

    choice = input("Select an option [1-5]: ").strip()
    if choice == "1":
        msg = input("Enter tweet message: ").strip()
        if not msg:
            print("Message cannot be empty.")
            return
        try:
            post_tweet(msg)
            print("Tweet sent successfully!")
        except Exception as e:
            print(f"Failed to post tweet: {e}", file=sys.stderr)
    elif choice == "2":
        msg = input("Enter tweet message: ").strip()
        if not msg:
            print("Message cannot be empty.")
            return
        mode = input("Schedule by [m]inutes or [t]ime (HH:MM)? ").strip().lower()
        try:
            if mode == "m":
                mins = int(input("Delay in minutes: ").strip())
                schedule_tweet(msg, delay_minutes=mins)
            elif mode == "t":
                hhmm = input("Time (HH:MM 24h): ").strip()
                schedule_tweet(msg, time_hhmm=hhmm)
            else:
                print("Invalid choice. Use 'm' or 't'.")
                return
            # Keep main thread alive until the scheduled tweet fires
            print("Waiting for scheduled tweet. Press Ctrl+C to abort.")
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nScheduling canceled.")
        except Exception as e:
            print(f"Failed to schedule tweet: {e}", file=sys.stderr)
    elif choice == "3":
        msg = input("Enter tweet message: ").strip()
        if not msg:
            print("Message cannot be empty.")
            return
        try:
            now = datetime.now()
            # Show the current month's calendar for convenience
            print("\n" + calendar.month(now.year, now.month))
            day = int(input("Day of month (1-31): ").strip())
            hhmm = input("Time (HH:MM 24h): ").strip()
            schedule_tweet_in_month(msg, now.year, now.month, day, hhmm)
            print("Waiting for scheduled tweet. Press Ctrl+C to abort.")
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nScheduling canceled.")
        except Exception as e:
            print(f"Failed to schedule tweet in month: {e}", file=sys.stderr)
    elif choice == "4":
        path = input("Path to .txt/.csv file: ").strip()
        try:
            mins = int(input("Delay between tweets (minutes): ").strip())
        except ValueError:
            print("Delay must be an integer number of minutes.")
            return
        try:
            bulk_post_from_file(path, mins)
        except Exception as e:
            print(f"Bulk post failed: {e}", file=sys.stderr)
    elif choice == "5":
        path = input("Path to .txt/.csv file: ").strip()
        try:
            mins = int(input("Frequency (minutes) between each scheduled post: ").strip())
        except ValueError:
            print("Frequency must be an integer number of minutes.")
            return
        try:
            tweets = read_tweets_from_file(path)
            if not tweets:
                print("No tweets found in file.")
                return
            timers: list[threading.Timer] = []
            for i, tmsg in enumerate(tweets):
                # schedule each subsequent tweet i*mins into the future
                try:
                    seconds = max(0, i * mins * 60)
                    def make_send(message):
                        def _send():
                            try:
                                post_tweet(message)
                                print("Tweet sent successfully!")
                            except Exception as e:
                                print(f"Scheduled bulk post failed: {e}", file=sys.stderr)
                        return _send
                    when = datetime.now() + timedelta(seconds=seconds)
                    print(f"Tweet scheduled for {when.strftime('%Y-%m-%d %H:%M')}...")
                    timer = threading.Timer(seconds, make_send(tmsg))
                    timer.daemon = True
                    timer.start()
                    timers.append(timer)
                except Exception as e:
                    print(f"Failed to schedule a tweet: {e}", file=sys.stderr)
            print("Bulk scheduler active. Press Ctrl+C to stop waiting.")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nStopped waiting for scheduled bulk posts.")
        except Exception as e:
            print(f"Bulk scheduler failed: {e}", file=sys.stderr)
    elif choice == "6":
        try:
            mins = int(input("Check interval (minutes): ").strip())
        except ValueError:
            print("Interval must be an integer number of minutes.")
            return
        reply = input("Auto-reply message: ").strip()
        if not reply:
            print("Reply message cannot be empty.")
            return
        try:
            auto_reply_to_mentions(mins, reply)
        except Exception as e:
            print(f"Auto-reply failed: {e}", file=sys.stderr)
    elif choice == "7":
        print("Goodbye!")
        return
    else:
        print("Invalid option. Please choose 1-7.")


def _get_message_from_argv_or_prompt(argv: list[str]) -> Optional[str]:
    # Join all args to allow spaces without quotes if desired
    msg = " ".join(argv[1:]).strip() if len(argv) > 1 else ""
    if msg:
        return msg
    try:
        return input("Enter tweet message: ").strip()
    except (EOFError, KeyboardInterrupt):
        return None


def main(argv: list[str]) -> int:
    if not _credentials_are_valid():
        print(
            "Error: Please set API_KEY, API_SECRET, ACCESS_TOKEN, and ACCESS_TOKEN_SECRET in tweet.py (from developer.x.com) and ensure your app has write permissions.",
            file=sys.stderr,
        )
        return 1

    # If a message is given as CLI args, keep existing behavior: post immediately
    message = " ".join(argv[1:]).strip() if len(argv) > 1 else ""
    if message:
        try:
            post_tweet(message)
        except tweepy.Unauthorized as e:
            print(f"Authentication failed (Unauthorized): {e}", file=sys.stderr)
            return 1
        except tweepy.Forbidden as e:
            print(f"Permission error (Forbidden): {e}", file=sys.stderr)
            return 1
        except tweepy.TooManyRequests as e:
            print(f"Rate limit exceeded: {e}", file=sys.stderr)
            return 1
        except tweepy.TweepyException as e:
            print(f"Twitter API error: {e}", file=sys.stderr)
            return 1
        except ValueError as e:
            print(f"Input error: {e}", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"Unexpected error: {e}", file=sys.stderr)
            return 1
        print("Tweet sent successfully!")
        return 0

    # Otherwise, show interactive menu
    try:
        _interactive_menu()
        return 0
    except KeyboardInterrupt:
        print("\nExiting.")
        return 0
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1

    try:
        post_tweet(message)
    except tweepy.Unauthorized as e:
        print(f"Authentication failed (Unauthorized): {e}", file=sys.stderr)
        return 1
    except tweepy.Forbidden as e:
        print(f"Permission error (Forbidden): {e}", file=sys.stderr)
        return 1
    except tweepy.TooManyRequests as e:
        print(f"Rate limit exceeded: {e}", file=sys.stderr)
        return 1
    except tweepy.TweepyException as e:
        print(f"Twitter API error: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"Input error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1

    print("Tweet sent successfully!")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
