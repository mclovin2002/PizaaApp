# Tweet script (Tweepy)

A minimal Python script to post a tweet using Tweepy and the official X (Twitter) API.

## Setup

1. Create a developer account and app at https://developer.x.com/
2. Generate your credentials and ensure your App has write permissions:
   - API Key
   - API Secret
   - Access Token
   - Access Token Secret
3. Provide credentials in one of the following ways:
   - Quick start: open `twitter_credentials.py` and paste your credentials into the placeholders, or
   - Use environment variables before running: `API_KEY`, `API_SECRET`, `ACCESS_TOKEN`, `ACCESS_TOKEN_SECRET`.

## Install dependencies

```bash
python -m pip install -r requirements.txt
```

## Run

- With a message as an argument:

```bash
python tweet.py "Hello from Tweepy!"
```

- Or run without arguments and you will be prompted to enter your tweet:

```bash
python tweet.py
```

If the tweet succeeds, you will see: `Tweet sent successfully!`.

## Notes
- Uses OAuth 1.0a with user context via Tweepy.
- Errors such as authentication failures, permission issues, and rate limits are handled with clear messages.
- Credentials are centralized in `twitter_credentials.py` and can optionally be read from environment variables.
