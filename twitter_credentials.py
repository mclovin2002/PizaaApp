"""
Centralized credentials loader for X (Twitter) API.

Where to get credentials:
- Create a developer account at https://developer.x.com/
- Create a Project + App in the Developer Portal
- Generate API Key, API Secret, Access Token, and Access Token Secret
- Ensure the app has write permissions to post tweets

How to provide credentials (choose ONE):
1) Edit the constants below and paste your keys/tokens, or
2) Set environment variables before running the script:
   - API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET
"""

from __future__ import annotations

import os
from typing import Tuple


# Option A: paste credentials here (recommended for quick local tests)
API_KEY: str = "YOUR_API_KEY"
API_SECRET: str = "YOUR_API_SECRET"
ACCESS_TOKEN: str = "YOUR_ACCESS_TOKEN"
ACCESS_TOKEN_SECRET: str = "YOUR_ACCESS_TOKEN_SECRET"


PLACEHOLDERS = {
    "YOUR_API_KEY",
    "YOUR_API_SECRET",
    "YOUR_ACCESS_TOKEN",
    "YOUR_ACCESS_TOKEN_SECRET",
}


def load_credentials() -> Tuple[str, str, str, str]:
    """Load credentials from environment variables or constants.

    Order of precedence for each value: environment variable -> constant above.

    Returns:
        Tuple of (api_key, api_secret, access_token, access_token_secret)

    Raises:
        ValueError: If any credential is missing or left as a placeholder.
    """
    api_key = os.getenv("API_KEY") or API_KEY
    api_secret = os.getenv("API_SECRET") or API_SECRET
    access_token = os.getenv("ACCESS_TOKEN") or ACCESS_TOKEN
    access_token_secret = os.getenv("ACCESS_TOKEN_SECRET") or ACCESS_TOKEN_SECRET

    values = {
        "API_KEY": api_key,
        "API_SECRET": api_secret,
        "ACCESS_TOKEN": access_token,
        "ACCESS_TOKEN_SECRET": access_token_secret,
    }

    missing = [k for k, v in values.items() if not v or v in PLACEHOLDERS]
    if missing:
        raise ValueError(
            "Missing or placeholder credentials for: " + ", ".join(missing)
        )

    return api_key, api_secret, access_token, access_token_secret


__all__ = ["load_credentials"]
