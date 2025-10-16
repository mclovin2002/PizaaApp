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
from typing import Optional

import tweepy
from twitter_credentials import load_credentials


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

    message = _get_message_from_argv_or_prompt(argv)
    if not message:
        print("Error: No tweet message provided.", file=sys.stderr)
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
