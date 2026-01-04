# API Setup Guide

This guide will help you obtain the required API credentials to run ResearchAI.

## Required API Keys

You need two sets of credentials:
1. Anthropic API Key (for Claude AI)
2. Reddit API Credentials (for searching Reddit)

---

## 1. Getting Your Anthropic API Key

### Step 1: Create an Anthropic Account

1. Visit https://console.anthropic.com/
2. Click "Sign Up" or "Sign In"
3. Create an account using your email or Google account

### Step 2: Get Your API Key

1. Once logged in, go to https://console.anthropic.com/settings/keys
2. Click "Create Key"
3. Give it a name (e.g., "ResearchAI")
4. Copy the API key (it starts with `sk-ant-`)
5. **IMPORTANT**: Save this key securely - you won't be able to see it again!

### Step 3: Add Credits (if needed)

- Anthropic provides some free credits for new accounts
- If you need more, go to https://console.anthropic.com/settings/billing
- Add a payment method and purchase credits

**Your Anthropic API key will look like:**
```
sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

## 2. Getting Your Reddit API Credentials

### Step 1: Create a Reddit Account

1. Go to https://www.reddit.com/
2. Sign up for an account if you don't have one
3. Verify your email address

**Note**: Reddit may require you to request API access and explain your use case. This approval process can take some time (hours to days).

### Step 2: Create a Reddit App

1. Visit https://www.reddit.com/prefs/apps
2. Scroll to the bottom and click "create another app..."
3. Fill in the form:
   - **name**: ResearchAI (or any name you like)
   - **App type**: Select "script"
   - **description**: AI-powered research tool (optional)
   - **about url**: Leave blank (optional)
   - **redirect uri**: http://localhost:8000 (required, but not used)
4. Click "create app"

### Step 3: Get Your Credentials

After creating the app, you'll see:

```
ResearchAI
personal use script
[YOUR_CLIENT_ID]          ← This is your CLIENT_ID (under "personal use script")

secret: [YOUR_SECRET]      ← This is your CLIENT_SECRET
```

**Your Reddit credentials will look like:**
- `REDDIT_CLIENT_ID`: `abc123XYZ789` (14 characters)
- `REDDIT_CLIENT_SECRET`: `xYz123AbC456DeF789` (27 characters)

---

## 3. Setting Up Your .env File

Once you have all credentials:

1. Copy the example file:
   ```bash
   cp .env.example .env
   ```

2. Open `.env` in a text editor:
   ```bash
   nano .env
   # or
   vim .env
   # or use any text editor
   ```

3. Fill in your credentials:
   ```env
   # Anthropic API Key
   ANTHROPIC_API_KEY=sk-ant-api03-your-actual-key-here

   # Reddit API Credentials
   REDDIT_CLIENT_ID=your_client_id_here
   REDDIT_CLIENT_SECRET=your_client_secret_here
   REDDIT_USER_AGENT=ResearchAI/0.1.0

   # FastAPI Settings
   DEBUG=True
   ```

4. Save the file

---

## 4. Verify Your Setup

Run this command to check if your .env file is properly configured:

```bash
python -c "from app.config import get_settings; s = get_settings(); print('✓ Config loaded successfully')"
```

If you see errors, double-check your .env file formatting.

---

## 5. Install Dependencies & Run

```bash
# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn app.main:app --reload

# Test the API
python test_research.py
```

---

## Troubleshooting

### "Invalid API Key" Error (Anthropic)
- Double-check you copied the entire key including `sk-ant-api03-`
- Make sure there are no extra spaces or quotes
- Verify the key is active at https://console.anthropic.com/settings/keys

### "Invalid Credentials" Error (Reddit)
- Verify your CLIENT_ID and CLIENT_SECRET are correct
- Make sure you selected "script" as the app type
- Check there are no extra spaces in your .env file

### "Module not found" Errors
- Run: `pip install -r requirements.txt`
- Make sure you're in the correct directory

### Rate Limiting
- Reddit API has rate limits (60 requests per minute)
- Anthropic has usage limits based on your tier
- If you hit limits, wait a few minutes and try again

---

## Cost Estimation

### Anthropic (Claude API)
- Model: Claude 3.5 Sonnet
- Input: ~$3 per million tokens
- Output: ~$15 per million tokens
- **Typical cost per research query**: $0.01 - $0.05

### Reddit API
- **Free** (with rate limits)
- 60 requests per minute for scripts

---

## Security Best Practices

1. **Never commit your .env file to Git**
   - It's already in .gitignore
   - Keep your API keys private

2. **Rotate keys regularly**
   - Change your API keys every few months
   - Immediately rotate if you suspect compromise

3. **Use environment-specific keys**
   - Use different keys for development and production
   - Never use production keys in testing

---

## Next Steps

Once you have your credentials configured:

1. Test the health endpoint: `curl http://localhost:8000/health`
2. Run a research query: `python test_research.py`
3. Explore the API docs: http://localhost:8000/docs

Happy researching!
