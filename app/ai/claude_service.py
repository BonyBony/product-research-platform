from anthropic import Anthropic
from typing import List, Dict
import json
from app.config import get_settings
from app.models.research import PainPoint, SeverityLevel


class ClaudeService:
    def __init__(self):
        settings = get_settings()
        self.client = Anthropic(api_key=settings.anthropic_api_key)
        self.model = "claude-sonnet-4-5"  # Latest Claude Sonnet 4.5 (auto-updates)

    def extract_pain_points(
        self,
        reddit_posts: List[Dict],
        problem_statement: str,
        target_users: str
    ) -> List[PainPoint]:
        """
        Use Claude to extract pain points from Reddit posts and comments.
        """
        if not reddit_posts:
            return []

        # Prepare the context from Reddit data
        context = self._prepare_context(reddit_posts)

        # Create the prompt
        prompt = self._create_extraction_prompt(
            context,
            problem_statement,
            target_users
        )

        # Call Claude API
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4000,
            temperature=0.3,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        # Parse the response
        # Handle different response formats from Anthropic API
        try:
            if hasattr(response.content[0], 'text'):
                response_text = response.content[0].text
            elif isinstance(response.content[0], dict):
                response_text = response.content[0].get('text', '')
            else:
                response_text = str(response.content[0])
        except (IndexError, AttributeError, TypeError) as e:
            print(f"Error accessing response text: {e}")
            return []

        pain_points = self._parse_response(response_text, reddit_posts)

        return pain_points

    def _prepare_context(self, reddit_posts: List[Dict]) -> str:
        """
        Format Reddit posts and comments into a context string.
        """
        context_parts = []

        for idx, post in enumerate(reddit_posts, 1):
            context_parts.append(f"\n--- POST {idx} ---")
            context_parts.append(f"Subreddit: r/{post['subreddit']}")
            context_parts.append(f"Title: {post['title']}")
            context_parts.append(f"URL: {post['url']}")

            if post.get('selftext'):
                context_parts.append(f"Content: {post['selftext'][:500]}")

            if post.get('comments'):
                context_parts.append(f"\nTop Comments:")
                for comment in post['comments']:
                    # Handle both 'body' (YouTube, HackerNews) and 'text' (Reddit) formats
                    comment_text = comment.get('body') or comment.get('text', '')
                    if comment_text:
                        context_parts.append(f"- {comment_text[:300]}")

        return "\n".join(context_parts)

    def _create_extraction_prompt(
        self,
        context: str,
        problem_statement: str,
        target_users: str
    ) -> str:
        """
        Create the prompt for Claude to extract pain points.
        """
        return f"""You are a product research analyst. Analyze the following Reddit posts and comments to extract specific pain points related to the problem statement.

Problem Statement: {problem_statement}
Target Users: {target_users}

Reddit Data:
{context}

Your task:
1. Identify distinct pain points that users express
2. For each pain point, extract a direct quote from the Reddit data
3. Assess the severity (Low, Medium, or High) based on:
   - High: Critical problems that block users or cause significant frustration
   - Medium: Notable inconveniences that affect user experience
   - Low: Minor annoyances or nice-to-have improvements
4. Identify the source URL for each pain point

Return your analysis as a JSON array with this exact structure:
[
  {{
    "description": "Clear 1-sentence description of the pain point",
    "quote": "Exact quote from a user that demonstrates this pain point",
    "severity": "Low|Medium|High",
    "source_url": "Reddit post URL",
    "frequency": 1
  }}
]

Rules:
- Only extract pain points that are clearly related to the problem statement
- Use actual quotes from the Reddit data
- Each pain point should be distinct (no duplicates)
- Be specific and actionable in descriptions
- Return ONLY the JSON array, no additional text

JSON Output:"""

    def _parse_response(self, response_text: str, reddit_posts: List[Dict]) -> List[PainPoint]:
        """
        Parse Claude's response into PainPoint objects.
        """
        try:
            # Extract JSON from response
            response_text = response_text.strip()

            # Try to find JSON array in the response
            start_idx = response_text.find('[')
            end_idx = response_text.rfind(']') + 1

            if start_idx == -1 or end_idx == 0:
                return []

            json_str = response_text[start_idx:end_idx]
            pain_points_data = json.loads(json_str)

            # Convert to PainPoint objects
            pain_points = []
            for data in pain_points_data:
                try:
                    # Validate severity
                    severity = data.get('severity', 'Medium')
                    if severity not in ['Low', 'Medium', 'High']:
                        severity = 'Medium'

                    pain_point = PainPoint(
                        description=data.get('description', ''),
                        quote=data.get('quote', ''),
                        severity=SeverityLevel(severity),
                        source_url=data.get('source_url', ''),
                        frequency=data.get('frequency', 1)
                    )
                    pain_points.append(pain_point)
                except Exception:
                    continue

            return pain_points

        except json.JSONDecodeError:
            return []
        except Exception:
            return []
