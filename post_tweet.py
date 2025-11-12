"""
X (Twitter) API v2 Tweet Posting Script for Sashimi App
Automates posting text tweets and tweets with images using OAuth 1.0a

Requirements:
pip install tweepy python-dotenv

Usage:
1. Update .env with your OAuth 1.0a credentials
2. Run: python post_tweet.py
"""

import os
import tweepy
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Load credentials from .env
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")

def check_credentials():
    """Check if all required credentials are provided."""
    missing = []
    if not API_KEY:
        missing.append("API_KEY")
    if not API_SECRET:
        missing.append("API_SECRET")
    if not ACCESS_TOKEN:
        missing.append("ACCESS_TOKEN")
    if not ACCESS_TOKEN_SECRET:
        missing.append("ACCESS_TOKEN_SECRET")
    if missing:
        raise ValueError(f"Missing credentials in .env: {', '.join(missing)}")

def get_client():
    """Create and return Twitter API v2 client."""
    check_credentials()
    return tweepy.Client(
        consumer_key=API_KEY,
        consumer_secret=API_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET
    )

def post_tweet(text):
    """
    Post a text tweet using X API v2.

    Args:
        text (str): The text content of the tweet (max 280 characters)

    Returns:
        dict: Response containing tweet data, or None if failed
    """
    try:
        client = get_client()
        response = client.create_tweet(text=text)

        tweet_id = response.data["id"]
        tweet_url = f"https://x.com/i/status/{tweet_id}"

        print("✅ Tweet posted successfully!")
        print(f"📝 Tweet ID: {tweet_id}")
        print(f"🔗 Tweet URL: {tweet_url}")

        return response.data

    except tweepy.TweepyException as e:
        print(f"❌ Failed to post tweet: {e}")
        return None

def post_tweet_with_image(text, image_path):
    """
    Post a tweet with an attached image.

    Args:
        text (str): The text content of the tweet
        image_path (str): Path to the image file to attach

    Returns:
        dict: Response containing tweet data, or None if failed
    """
    try:
        # First upload the media using v1.1 API
        auth = tweepy.OAuth1UserHandler(
            API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET
        )
        api = tweepy.API(auth)
        media = api.media_upload(image_path)
        media_id = media.media_id

        # Then post the tweet with media
        client = get_client()
        response = client.create_tweet(text=text, media_ids=[media_id])

        tweet_id = response.data["id"]
        tweet_url = f"https://x.com/i/status/{tweet_id}"

        print("✅ Tweet with image posted successfully!")
        print(f"📝 Tweet ID: {tweet_id}")
        print(f"🔗 Tweet URL: {tweet_url}")

        return response.data

    except tweepy.TweepyException as e:
        print(f"❌ Failed to post tweet with image: {e}")
        return None
    except FileNotFoundError:
        print(f"❌ Image file not found: {image_path}")
        return None

# Example usage
if __name__ == "__main__":
    # Test posting a text tweet
    post_tweet("Testing automated posting from Sashimi App 🚀")

    # Uncomment to test with image (replace with actual image path)
    # post_tweet_with_image("Testing tweet with image from Sashimi App 🖼️", "path/to/your/image.jpg")