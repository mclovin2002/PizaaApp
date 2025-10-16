# PizzaApp Quick Start Guide 🍕

Welcome to PizzaApp - your professional Twitter posting suite!

## Installation

1. **Install dependencies**:
   ```bash
   cd /Users/arash/Desktop/SahimiApp/PizaaApp
   python3 -m pip install -r requirements.txt
   ```

2. **Generate logo** (if not already created):
   ```bash
   python3 generate_logo.py
   ```

## Launch the App

```bash
python3 gui.py
```

## First Time Setup

When you launch the app for the first time, you'll see a credential setup screen:

1. Go to https://developer.x.com/ and create a developer account
2. Create a new Project and App
3. Generate API credentials with **Read and Write** permissions
4. Copy your credentials:
   - API Key
   - API Secret  
   - Access Token
   - Access Token Secret
5. Paste them into the PizzaApp setup form
6. Click "Save and Continue"

That's it! Your credentials are saved and you're ready to use all features.

## Using the App

### Quick Post
1. Click the "📝 Post Now" tab
2. Type your tweet
3. Click "Post Tweet"
✅ Done!

### Schedule a Tweet
1. Click "⏰ Schedule" tab
2. Type your message
3. Choose when:
   - **Minutes from now**: Enter number of minutes
   - **Today at time**: Enter HH:MM (24-hour format)
   - **Day of month**: Enter day number (1-31) and time
4. Click "Schedule Tweet"
✅ Your tweet is scheduled!

### Bulk Operations
1. Create a text file with one tweet per line:
   ```
   First tweet here
   Second tweet here
   Third tweet here
   ```
2. Click "📦 Bulk" tab
3. Click "Browse" and select your file
4. Choose operation:
   - **Post immediately**: Posts each tweet with a delay between them
   - **Schedule with frequency**: Schedules all tweets into the future
5. Set delay/frequency in minutes
6. Click "Execute Bulk Operation"
✅ All tweets posted or scheduled!

### Auto-Reply to Mentions
1. Click "🔄 Auto-Reply" tab
2. Set check interval (how often to check for new mentions)
3. Type your auto-reply message
4. Click "Start Auto-Reply"
✅ The app will now reply to new mentions automatically!

To stop: Click "Stop Auto-Reply"

## Troubleshooting

### "Authentication failed"
- Check your credentials in Settings tab
- Click "Reconfigure Credentials"
- Ensure your app has Read and Write permissions on developer.x.com

### "Rate limit exceeded"
- Twitter has limits on how many tweets you can post
- Wait a few minutes and try again
- Reduce frequency for bulk operations

### Logo not showing
- Run: `python3 generate_logo.py`
- Make sure Pillow is installed

## Pro Tips

💡 **Schedule wisely**: Use the monthly calendar view to plan tweets ahead

💡 **Test first**: Post a test tweet to verify your credentials work

💡 **Bulk posting**: Use delays of at least 1 minute to avoid rate limits

💡 **Auto-reply**: Start with longer intervals (5+ minutes) to stay within limits

💡 **File format**: CSV files use the first column as the tweet text

## Need Help?

Check out:
- `README.md` - Complete documentation
- `GUI_OVERVIEW.md` - Visual design details
- `tweet.py` - CLI mode with interactive menu

## Features at a Glance

✅ Credential management with secure storage
✅ Instant tweet posting
✅ Flexible scheduling (minutes, time, monthly)
✅ Bulk operations from files
✅ Auto-reply to mentions
✅ Professional, minimalistic design
✅ Custom pizza logo with bite 🍕
✅ Clean error messages
✅ Background processing
✅ No crashes or freezes

Enjoy using PizzaApp! 🍕✨
