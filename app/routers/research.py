from fastapi import APIRouter, HTTPException, status
from app.models.research import ResearchRequest, ResearchResponse, DataSource
from app.services.reddit_service import RedditService
from app.services.mock_reddit_service import MockRedditService
from app.services.youtube_service import YouTubeService
from app.services.hackernews_service import HackerNewsService
from app.services.producthunt_service import ProductHuntService
from app.ai.claude_service import ClaudeService
from app.ai.mock_claude_service import MockClaudeService
from app.config import get_settings

router = APIRouter(
    prefix="/api",
    tags=["research"]
)


@router.post("/research", response_model=ResearchResponse, status_code=status.HTTP_200_OK)
async def research_pain_points(request: ResearchRequest):
    """
    Research pain points from online discussions using AI.

    This endpoint:
    1. Searches various platforms for content related to the problem statement
    2. Collects top posts/videos and their comments/discussions
    3. Uses Claude AI to extract and structure pain points
    4. Returns actionable insights for product managers

    DATA SOURCES:
    - AUTO (default): Automatically selects based on available API keys
      Priority: YouTube > HackerNews > Reddit > ProductHunt > Demo
      YouTube preferred for consumer products, HackerNews for tech/developer products
    - YOUTUBE: YouTube comments - best for consumer products and apps (requires API key)
    - HACKERNEWS: Hacker News discussions - best for tech/developer products (free, no API key needed)
    - REDDIT: Reddit discussions (requires API credentials)
    - PRODUCTHUNT: Product Hunt reviews (requires API token)
    - DEMO: Mock data for testing

    Args:
        request: ResearchRequest containing problem_statement, target_users, and optional source

    Returns:
        ResearchResponse with extracted pain points and analysis metadata
    """
    try:
        settings = get_settings()

        # Choose data source service
        data_service, source_name = _select_data_source(request.source, settings)

        # Choose Claude service based on configuration
        # Only use real Claude if we have API key AND not in demo mode
        if settings.demo_mode or not settings.anthropic_api_key:
            claude_service = MockClaudeService()
        else:
            claude_service = ClaudeService()

        # Search for relevant content
        # Handle different method signatures (search vs search_posts)
        if hasattr(data_service, 'search'):
            # HackerNews, ProductHunt use search()
            posts = data_service.search(
                problem_statement=request.problem_statement,
                target_users=request.target_users,
                max_results=20
            )
        else:
            # YouTube, Reddit, Mock use search_posts()
            posts = data_service.search_posts(
                problem_statement=request.problem_statement,
                target_users=request.target_users,
                max_posts=20,
                max_comments_per_post=5,
                days_back=30
            )

        if not posts:
            return ResearchResponse(
                pain_points=[],
                total_posts_analyzed=0,
                total_comments_analyzed=0
            )

        # Calculate stats
        total_comments = sum(len(post.get('comments', [])) for post in posts)

        # Extract pain points using Claude AI
        pain_points = claude_service.extract_pain_points(
            reddit_posts=posts,  # Variable name kept for compatibility
            problem_statement=request.problem_statement,
            target_users=request.target_users
        )

        return ResearchResponse(
            pain_points=pain_points,
            total_posts_analyzed=len(posts),
            total_comments_analyzed=total_comments
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to research pain points: {str(e)}"
        )


def _select_data_source(source: DataSource, settings):
    """
    Select the appropriate data source service based on user choice and available API keys.

    Returns:
        Tuple of (service_instance, source_name)
    """
    # If specific source requested, use it
    if source == DataSource.YOUTUBE:
        if not settings.youtube_api_key:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="YouTube API key not configured. Add YOUTUBE_API_KEY to .env"
            )
        return YouTubeService(), "YouTube"

    elif source == DataSource.REDDIT:
        if not settings.reddit_client_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reddit API credentials not configured. Add REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET to .env"
            )
        return RedditService(), "Reddit"

    elif source == DataSource.HACKERNEWS:
        return HackerNewsService(), "HackerNews"

    elif source == DataSource.PRODUCTHUNT:
        if not settings.producthunt_api_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product Hunt API token not configured. Add PRODUCTHUNT_API_TOKEN to .env"
            )
        return ProductHuntService(), "ProductHunt"

    elif source == DataSource.DEMO:
        return MockRedditService(), "Demo"

    # AUTO mode: select best available source
    # Priority: YouTube > HackerNews > Reddit > ProductHunt > Demo
    # YouTube is preferred for broader coverage of consumer products
    elif source == DataSource.AUTO:
        if settings.youtube_api_key:
            return YouTubeService(), "YouTube (auto)"
        # HackerNews is always available (no API key needed) - good for tech topics
        return HackerNewsService(), "HackerNews (auto)"

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid data source: {source}"
        )
