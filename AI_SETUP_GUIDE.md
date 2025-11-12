# AI-Powered Auto-Reply Setup Guide

SashimiApp now supports **AI-generated contextual replies** to Twitter mentions! Instead of sending the same fixed message to everyone, the AI reads each mention and generates a personalized, contextual response.

## 🎯 Overview

**What changed:**
- **Before:** Auto-reply sent the same message to all mentions
- **Now:** AI reads each mention and generates a unique, contextual reply

**Supported AI Providers:**
1. **Anthropic Claude** (Recommended - most intelligent)
2. **OpenAI GPT** (GPT-4, GPT-3.5)
3. **Groq** (Fastest - free tier available)
4. **Ollama** (Local/private - no API key needed)
5. **Template fallback** (No AI, smart keyword matching)

---

## 🚀 Quick Start

### Option 1: Using Anthropic Claude (Recommended)

1. **Get API Key:**
   - Go to https://console.anthropic.com/
   - Sign up and get your API key
   - Free tier: $5 credit to start

2. **Set Environment Variable:**
   ```bash
   export ANTHROPIC_API_KEY="your-api-key-here"
   ```

3. **Install Dependencies:**
   ```bash
   pip install anthropic
   ```

4. **Use in GUI:**
   - Click "🤖 Auto Reply" card
   - Select "Anthropic Claude" from radio buttons
   - Add optional brand context (e.g., "We're a sushi delivery app")
   - Click "🚀 Start Auto Reply"

### Option 2: Using OpenAI

1. **Get API Key:**
   - Go to https://platform.openai.com/api-keys
   - Create an API key
   - Note: Requires payment setup

2. **Set Environment Variable:**
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

3. **Install Dependencies:**
   ```bash
   pip install openai
   ```

4. **Use in GUI:**
   - Select "OpenAI GPT-4" as provider
   - Uses GPT-4 Turbo by default

### Option 3: Using Groq (Fastest & Free)

1. **Get API Key:**
   - Go to https://console.groq.com/
   - Sign up for free tier
   - Get your API key

2. **Set Environment Variable:**
   ```bash
   export GROQ_API_KEY="your-api-key-here"
   ```

3. **Install Dependencies:**
   ```bash
   pip install groq
   ```

4. **Use in GUI:**
   - Select "Groq (Fast & Free)" as provider
   - Very fast responses, good quality

### Option 4: Using Ollama (100% Local/Private)

1. **Install Ollama:**
   ```bash
   # macOS/Linux
   curl -fsSL https://ollama.com/install.sh | sh

   # Or download from https://ollama.com/download
   ```

2. **Pull a Model:**
   ```bash
   ollama pull llama3.2
   ```

3. **Install Python Package:**
   ```bash
   pip install ollama
   ```

4. **Use in GUI:**
   - Select "Ollama (Local)" as provider
   - No API key needed (runs on your computer)
   - Completely private - no data sent to cloud

### Option 5: Template Mode (No AI)

- Select "None (Template-based)" as provider
- Uses smart keyword matching
- No API key or installation needed
- Good fallback option

---

## 📋 How It Works

### AI Mode Flow:

1. **Mention Detected:**
   ```
   @YourAccount Hey, loving your sushi app! Can you add more fish options? 🍣
   ```

2. **AI Analyzes Context:**
   - Reads the mention text
   - Understands it's a feature request
   - Considers your brand context
   - Matches the friendly tone

3. **Generated Reply:**
   ```
   @user Thanks so much! 😊 Great suggestion - we're always looking to expand our fish selection.
   I'll pass this along to our team. In the meantime, feel free to check out our current 20+ fish options!
   ```

### Traditional Mode Flow:

1. **Mention Detected:**
   ```
   @YourAccount [any mention]
   ```

2. **Fixed Reply Sent:**
   ```
   @user Thanks for reaching out!
   ```

---

## ⚙️ Configuration Options

### In the GUI:

When you click "🤖 Auto Reply", you'll see:

| Option | Description | Example |
|--------|-------------|---------|
| **AI Provider** | Which AI service to use | `Anthropic Claude` |
| **Check Interval** | How often to check for mentions (minutes) | `5` |
| **Brand Context** | Optional context for AI | `"We're a sushi delivery app in NYC"` |

### Advanced: Using CLI

You can also use the AI auto-reply from the command line:

```python
from ai_reply_generator import create_reply_generator_from_config

# AI mode
generator = create_reply_generator_from_config("anthropic")
reply = generator.generate_reply(
    mention_text="Hey, loving your app! Can you add dark mode?",
    mention_author="techfan123",
    context="We're a sushi delivery app focused on fresh ingredients"
)
print(reply)
```

---

## 🎨 Customizing AI Behavior

### 1. Brand Context

Adding brand context helps the AI understand your business:

```
Good context examples:
- "We're a sushi delivery app focused on quality ingredients"
- "Tech startup building automation tools for Twitter"
- "Indie game developer making retro-style platformers"
```

The AI will use this to:
- Give accurate information
- Match your brand voice
- Provide relevant responses

### 2. Editing System Prompt (Advanced)

To customize how the AI behaves, edit [ai_reply_generator.py](ai_reply_generator.py):

```python
def _get_default_system_prompt(self) -> str:
    return """Your custom instructions here.

    For example:
    - Always be professional but friendly
    - Use emojis sparingly
    - Keep responses under 200 characters
    - Never discuss pricing (direct to website)
    """
```

### 3. Model Selection

Different models have different characteristics:

| Provider | Model | Speed | Quality | Cost |
|----------|-------|-------|---------|------|
| Anthropic | claude-3-5-sonnet | Fast | Excellent | $3/M tokens |
| OpenAI | gpt-4-turbo | Medium | Excellent | $10/M tokens |
| Groq | llama-3.3-70b | Very Fast | Good | Free tier |
| Ollama | llama3.2 | Medium | Good | Free (local) |

To change model:

```python
ai_generator = create_reply_generator_from_config(
    provider_name="openai",
    model="gpt-3.5-turbo"  # Cheaper, faster, still good
)
```

---

## 💰 Cost Estimates

### Typical Auto-Reply Usage:

**Scenario:** 50 mentions per day

| Provider | Cost per Day | Cost per Month |
|----------|--------------|----------------|
| Anthropic Claude | ~$0.15 | ~$4.50 |
| OpenAI GPT-4 | ~$0.50 | ~$15.00 |
| OpenAI GPT-3.5 | ~$0.05 | ~$1.50 |
| Groq | Free (rate limited) | Free |
| Ollama | $0 (local) | $0 |

**Note:** Prices vary based on token usage. These are estimates for typical mention replies.

---

## 🔒 Security & Privacy

### API Keys:

- **Never commit API keys to git**
- Always use environment variables
- Rotate keys if exposed

### Data Privacy:

| Provider | Data Sent | Privacy Level |
|----------|-----------|---------------|
| Anthropic | Mention text only | Not used for training |
| OpenAI | Mention text only | Can opt-out of training |
| Groq | Mention text only | Check terms of service |
| Ollama | Nothing (local) | 100% private |

### Recommendation:

- For sensitive accounts: Use **Ollama** (completely local)
- For general use: **Anthropic** or **OpenAI** are fine
- Always review AI responses periodically

---

## 🧪 Testing AI Replies

### Test Locally Without Twitter:

```python
from ai_reply_generator import create_reply_generator_from_config

# Test your AI setup
generator = create_reply_generator_from_config("anthropic")

test_mentions = [
    "Hey, your app is broken!",
    "Thanks so much for the help!",
    "Can you add dark mode?",
]

for mention in test_mentions:
    reply = generator.generate_reply(
        mention_text=mention,
        mention_author="testuser",
        context="We're a sushi delivery app"
    )
    print(f"Mention: {mention}")
    print(f"Reply: {reply}\n")
```

---

## 🐛 Troubleshooting

### "API key not found"

**Solution:**
```bash
# Make sure you've exported the key in the same terminal
export ANTHROPIC_API_KEY="your-key"

# Then run the app from that same terminal
python sashimi_gui.py
```

### "Package not installed"

**Solution:**
```bash
# Install all AI dependencies
pip install openai anthropic groq ollama

# Or install just what you need
pip install anthropic
```

### "AI generation failed"

**Solution:**
- Check your API key is valid
- Check your internet connection
- Verify you have API credits remaining
- The app will automatically fall back to template replies

### Ollama "Connection refused"

**Solution:**
```bash
# Make sure Ollama is running
ollama serve

# In another terminal, test it
ollama run llama3.2 "hello"
```

---

## 📊 Monitoring AI Performance

### View AI Logs:

When auto-reply is running, you'll see:

```
🤖 [14:30:15] Starting AI auto-reply with anthropic (interval: 5 min)
   📝 Brand context: We're a sushi delivery app focused on fresh ingredients...
   🔧 Make sure to set your API key: ANTHROPIC_API_KEY
```

### Track Response Quality:

Periodically check your Twitter mentions to see:
- Are replies relevant?
- Are they too long/short?
- Do they match your brand voice?

Adjust the system prompt or brand context as needed.

---

## 🎯 Best Practices

### 1. Start Small
- Test with 1-2 hour intervals first
- Monitor responses carefully
- Adjust settings based on results

### 2. Set Boundaries
- Configure system prompt to avoid certain topics
- Add disclaimers for legal/medical questions
- Direct complex issues to DMs or support

### 3. Stay Authentic
- AI should enhance, not replace, your voice
- Review and refine the system prompt
- Add personality with brand context

### 4. Monitor Regularly
- Check replies daily at first
- Look for weird/inappropriate responses
- Update system prompt if needed

### 5. Have a Backup
- Keep fixed message mode as backup
- Test AI on non-critical accounts first
- Always have fallback enabled

---

## 📚 Example System Prompts

### For E-commerce:
```
You are a friendly customer service rep for a sushi delivery app.
Be helpful, warm, and professional. If someone asks about orders,
direct them to DM us. Always thank customers for feedback.
Keep responses under 240 characters.
```

### For Personal Brand:
```
You are responding as [Your Name], a developer sharing your work.
Be authentic and conversational. Thank people for their support.
For technical questions, offer to help but keep it brief.
Use casual language and occasional emojis.
```

### For Business Account:
```
You are the social media manager for [Company Name].
Stay professional but approachable. For support issues,
ask them to email support@company.com. For praise, thank warmly.
For questions, answer briefly or direct to docs.
```

---

## 🚀 What's Next?

Future improvements planned:
- [ ] Sentiment analysis before replying
- [ ] A/B testing different reply styles
- [ ] Reply templates for common questions
- [ ] Analytics dashboard for AI performance
- [ ] Multi-language support
- [ ] Voice/tone presets (formal, casual, funny)

---

## 📞 Support

**Issues with AI integration?**
- Check [ai_reply_generator.py](ai_reply_generator.py) for implementation details
- Test with `python ai_reply_generator.py` to debug
- Review provider documentation:
  - Anthropic: https://docs.anthropic.com/
  - OpenAI: https://platform.openai.com/docs
  - Groq: https://console.groq.com/docs
  - Ollama: https://ollama.com/docs

**Contributing:**
- Add new AI providers in `ai_reply_generator.py`
- Improve system prompts
- Share your best configurations!

---

**Happy auto-replying! 🤖🍣**

