# PizzaApp - Twitter Posting Suite 🍕

A professional, minimalistic GUI application for posting, scheduling, and managing tweets using Tweepy and the official X (Twitter) API.

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
python3 -m pip install -r requirements.txt
```

## Run the GUI

Launch the graphical interface:

```bash
python3 gui.py
```

On first launch, you'll be prompted to enter your API credentials through a clean, intuitive form. The app saves them securely to `twitter_credentials.py`.

## CLI Mode (Alternative)

You can still use the command-line interface:

- With a message as an argument:

```bash
python3 tweet.py "Hello from Tweepy!"
```

- Or run without arguments for an interactive menu:

```bash
python3 tweet.py
```

If the tweet succeeds, you will see: `Tweet sent successfully!`.

## Notes
- Uses OAuth 1.0a with user context via Tweepy.
- Errors such as authentication failures, permission issues, and rate limits are handled with clear messages.
- Credentials are centralized in `twitter_credentials.py` and can optionally be read from environment variables.

## GUI Features

The graphical interface includes:

### 📝 Post Now Tab
- Instant tweet posting with a clean text editor
- Character counter and validation

### ⏰ Schedule Tab
- **Minutes from now**: Schedule a tweet X minutes in the future
- **Today at time**: Schedule for a specific time (HH:MM) today
- **Day of month**: Pick a day in the current month with a visual calendar

### 📦 Bulk Tab
- Upload .txt or .csv files with multiple tweets
- **Post immediately**: Sequential posting with configurable delay
- **Schedule with frequency**: Schedules all tweets into the future at regular intervals

### 🔄 Auto-Reply Tab
- Automatically reply to new mentions
- Configure check interval and reply message
- Tracks last replied tweet to avoid duplicates
- Start/stop with one click

### ⚙️ Settings Tab
- Reconfigure API credentials anytime
- About information

## CLI Features (Advanced)

When running `tweet.py` without arguments, you get an interactive menu:

1. Post a tweet now
2. Schedule a tweet (by minutes or at HH:MM)
3. Schedule a tweet within the current month (pick day + time from calendar)
4. Bulk post from a .txt or .csv file (sequential, with delay between each)
5. Bulk scheduler (file + frequency minutes; schedules each line into the future)
6. Enable auto-reply mode (replies to new mentions every N minutes)
7. Exit

## Developer API

Advanced functions exposed in code:
- `post_tweet(message: str)` - Post immediately
- `schedule_tweet(message, delay_minutes=None, time_hhmm=None)` - Schedule a tweet
- `schedule_tweet_in_month(message, year, month, day, time_hhmm)` - Monthly scheduling
- `bulk_post_from_file(file_path, delay_minutes)` - Bulk post with delay
- `auto_reply_to_mentions(interval_minutes, reply_message, state_file)` - Auto-reply loop

## Tips
- The pizza logo has a bite taken out of it - a playful touch for your posting app!
- Monthly scheduler shows the current month's calendar for easy date selection
- Bulk scheduler keeps the app running to execute scheduled tweets
- All operations include comprehensive error handling for API failures
- Try `sample_tweets.txt` to test bulk posting features

## Quick Files Reference
- **gui.py** - Launch the graphical interface
- **tweet.py** - Command-line interface with interactive menu
- **twitter_credentials.py** - Credential storage (auto-managed by GUI)
- **twitter_utils.py** - Backend utilities
- **generate_logo.py** - Regenerate the pizza logo if needed
- **sample_tweets.txt** - Example file for testing bulk operations
- **QUICKSTART.md** - Step-by-step getting started guide
- **GUI_OVERVIEW.md** - Detailed UI documentation
