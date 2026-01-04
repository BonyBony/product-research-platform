# Demo Mode Guide

ResearchAI is now running in **DEMO MODE** with mock data! This allows you to test the full application without requiring API keys.

## What's Working Right Now

✅ FastAPI server is running at http://localhost:8000
✅ POST /api/research endpoint is fully functional
✅ Mock Reddit data with realistic user posts and comments
✅ Mock AI pain point extraction
✅ Complete API response structure

## Current Setup

Your `.env` file is configured for demo mode:

```env
DEMO_MODE=True
```

This means:
- **Reddit Service**: Using mock Reddit data (no Reddit API required)
- **Claude Service**: Using mock pain point extraction (no Anthropic API required)

## Testing the Demo

### Option 1: Use the Test Script

```bash
python3 test_research.py
```

This sends a sample request and displays formatted results.

### Option 2: Use cURL

```bash
curl -X POST http://localhost:8000/api/research \
  -H "Content-Type: application/json" \
  -d '{
    "problem_statement": "People struggle to find healthy meal options when working from home",
    "target_users": "Remote workers"
  }'
```

### Option 3: Use Swagger UI

Visit http://localhost:8000/docs in your browser for interactive API testing.

## Sample Results

The demo includes realistic mock data for:
- **Meal planning for remote workers** (default)
- Fitness challenges
- Productivity issues

Example pain points you'll see:
- Decision fatigue from meal planning
- Lack of structure leading to unhealthy choices
- Food waste from poor planning
- Expense of ordering takeout

## Switching to Production Mode

Once you receive your API credentials from Reddit and Anthropic:

### Option 1: Partial Production (Recommended First Step)

If you have **Anthropic API key** but still waiting for Reddit:

```env
DEMO_MODE=False
ANTHROPIC_API_KEY=sk-ant-api03-your-actual-key-here
# Reddit credentials still optional - will use mock data
```

This gives you:
- ✅ Real Claude AI extraction
- 📊 Mock Reddit data

### Option 2: Full Production

Once you have **both API keys**:

```env
DEMO_MODE=False
ANTHROPIC_API_KEY=sk-ant-api03-your-actual-key-here
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
```

This gives you:
- ✅ Real Reddit data
- ✅ Real Claude AI extraction

### After Updating .env

Restart the server:

```bash
# Stop the current server (Ctrl+C)
# Then restart:
python3 -m uvicorn app.main:app --reload
```

## How Demo Mode Works

The demo mode intelligently switches between services:

```python
# In app/routers/research.py
if settings.demo_mode or not settings.reddit_client_id:
    reddit_service = MockRedditService()  # Uses mock data
else:
    reddit_service = RedditService()       # Uses real Reddit API

if settings.demo_mode or not settings.anthropic_api_key:
    claude_service = MockClaudeService()   # Uses mock extraction
else:
    claude_service = ClaudeService()       # Uses real Claude API
```

This means you can:
- Start with full demo (no keys needed)
- Add Anthropic key → get real AI with mock Reddit
- Add both keys → get full production experience

## API Endpoints

### GET /health
Quick health check

```bash
curl http://localhost:8000/health
```

Response:
```json
{"status": "healthy"}
```

### GET /
API information

```bash
curl http://localhost:8000/
```

### POST /api/research
Main research endpoint (works in demo mode!)

## Mock Data Details

The mock Reddit service includes:
- 5 realistic posts about meal planning for remote workers
- 4-5 comments per post from "real" users
- Realistic upvote scores and metadata
- Authentic user pain points and frustrations

The mock Claude service:
- Extracts 6-8 pain points per query
- Assigns realistic severity levels (Low/Medium/High)
- Includes frequency counts
- Uses actual quotes from mock Reddit data

## Next Steps

1. ✅ You're already testing the demo!
2. ⏳ Wait for Reddit API approval
3. 🔑 Get your Anthropic API key from https://console.anthropic.com/
4. 🚀 Switch to production mode when ready

## Need Help?

- **API Setup**: See `API_SETUP_GUIDE.md`
- **Full README**: See `README.md`
- **API Docs**: http://localhost:8000/docs

## Files You Can Explore

**Mock Data Sources:**
- `app/services/mock_reddit_service.py` - Mock Reddit posts and comments
- `app/ai/mock_claude_service.py` - Mock pain point extraction

**Configuration:**
- `.env` - Your current settings (demo mode enabled)
- `app/config.py` - Configuration loader

**Main Endpoint:**
- `app/routers/research.py` - Research endpoint with demo mode logic

Enjoy testing ResearchAI! 🚀
