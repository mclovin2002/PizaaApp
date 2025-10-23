from __future__ import annotations

from typing import Optional

import os


def build_reply_prompt(user_spec: str, mention_text: str) -> str:
    """Create a short prompt for an AI to craft a reply based on user_spec and the mention content."""
    # This is intentionally simple and safe; consumers should plug their own API calls.
    prompt = (
        f"You are an assistant that crafts short, polite Twitter replies. "
        f"User wants to reply to: {user_spec}.\n"
        f"Original tweet: {mention_text}\n"
        "Write a single concise reply (<= 240 characters) that is friendly and on-topic."
    )
    return prompt


def generate_reply_via_api(prompt: str, api_key: Optional[str] = None) -> str:
    """Placeholder function to call an AI API and return text.

    The project owner should configure an API key (e.g., OpenAI) and replace this
    implementation with an actual call. For now it returns a deterministic stub.
    """
    # If an actual API is available, use it here. Return a short stub reply for now.
    return "Thanks for sharing — really interesting!"  # stubbed reply
