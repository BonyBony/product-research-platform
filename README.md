# ResearchAI

AI-powered product research assistant for Product Managers. Automatically extracts pain points from Reddit discussions using Claude AI.

## Project Structure

```
ai-product-portfolio/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── models/              # Pydantic models
│   ├── routers/             # API routes
│   │   └── health.py        # Health check endpoint
│   ├── services/            # Business logic
│   └── ai/                  # AI/LLM integrations
├── requirements.txt
├── .env.example
└── .gitignore
```

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your API credentials:

```bash
cp .env.example .env
```

Required credentials:
- **ANTHROPIC_API_KEY**: Get from https://console.anthropic.com/
- **REDDIT_CLIENT_ID**: Create app at https://www.reddit.com/prefs/apps
- **REDDIT_CLIENT_SECRET**: From your Reddit app
- **REDDIT_USER_AGENT**: Keep as ResearchAI/0.1.0

### 3. Run the Application

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### 4. Test the Health Endpoint

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "healthy"}
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### POST /api/research

Extract pain points from Reddit discussions using AI.

**Request Body:**
```json
{
  "problem_statement": "People struggle to find healthy meal options when working from home",
  "target_users": "Remote workers"
}
```

**Response:**
```json
{
  "pain_points": [
    {
      "description": "Users struggle to plan meals in advance",
      "quote": "I never know what to eat for lunch and end up ordering junk food",
      "severity": "Medium",
      "source_url": "https://reddit.com/r/...",
      "frequency": 1
    }
  ],
  "total_posts_analyzed": 20,
  "total_comments_analyzed": 87
}
```

### GET /health

Health check endpoint.

**Response:**
```json
{"status": "healthy"}
```

## Testing the API

### Using the Test Script

```bash
python test_research.py
```

This will send a sample request and display formatted results.

### Using cURL

```bash
curl -X POST http://localhost:8000/api/research \
  -H "Content-Type: application/json" \
  -d '{
    "problem_statement": "People struggle to find healthy meal options when working from home",
    "target_users": "Remote workers"
  }'
```

### Using Swagger UI

1. Navigate to http://localhost:8000/docs
2. Click on POST /api/research
3. Click "Try it out"
4. Enter your request body
5. Click "Execute"

## How It Works

1. **Reddit Search**: Searches Reddit for posts related to your problem statement
2. **Data Collection**: Gathers top 20 posts from the last month with their top 5 comments
3. **AI Analysis**: Uses Claude 3.5 Sonnet to extract and structure pain points
4. **Results**: Returns actionable insights with severity levels and direct user quotes
