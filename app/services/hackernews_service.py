import requests
from typing import List, Dict
import string
from datetime import datetime


class HackerNewsService:
    """
    Service to search Hacker News using Algolia HN Search API.
    Great for tech products, developer tools, and SaaS research.
    """

    def __init__(self):
        self.base_url = "https://hn.algolia.com/api/v1"

    def search(self, problem_statement: str, target_users: str, max_results: int = 20) -> List[Dict]:
        """
        Search Hacker News for stories and comments related to the problem.

        Args:
            problem_statement: The problem to research
            target_users: Target user segment
            max_results: Maximum number of stories to return

        Returns:
            List of stories with comments in Reddit-compatible format
        """
        keywords = self._extract_keywords(problem_statement, target_users)

        print("\n" + "=" * 60)
        print("HACKER NEWS SEARCH DEBUG")
        print("=" * 60)
        print(f"Original Problem: {problem_statement}")
        print(f"Target Users: {target_users}")
        print(f"Extracted Keywords: {keywords}")
        print(f"Final Search Query: {keywords}")
        print("=" * 60)

        stories = self._search_stories(keywords, max_results)

        print(f"\nStories found: {len(stories)}")
        if stories:
            print("First few story titles:")
            for idx, story in enumerate(stories[:5], 1):
                print(f"  {idx}. {story['title']}")
        print("=" * 60 + "\n")

        return stories

    def _extract_keywords(self, problem_statement: str, target_users: str) -> str:
        """
        Extract relevant keywords from problem statement and target users.
        Focus on tech/startup/developer terms for HackerNews.
        """
        # Stop words to remove (only truly generic words)
        stop_words = {
            'i', 'want', 'to', 'understand', 'what', 'are', 'the', 'a', 'an',
            'and', 'or', 'but', 'in', 'on', 'at', 'is', 'was', 'were', 'be',
            'of', 'for', 'with', 'as', 'by', 'this', 'that', 'from', 'have',
            'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
            'my', 'im', 'me', 'when', 'if', 'there', 'now', 'so', 'just', 'can',
            'also', 'some', 'one', 'get', 'let', 'like', 'which', 'feel', 'generally',
            'mostly', 'sometimes', 'etc'
        }

        # Combine text and convert to lowercase
        text = f"{problem_statement} {target_users}".lower()

        # Remove punctuation
        text = text.translate(str.maketrans('', '', string.punctuation))

        # Extract words, filter stop words
        words = [w for w in text.split() if w not in stop_words and len(w) > 2]

        # Keep up to 8 keywords for better context (fewer but more relevant)
        return ' '.join(words[:8])

    def _search_stories(self, query: str, max_results: int) -> List[Dict]:
        """
        Search for stories on Hacker News.
        """
        try:
            # Search for stories with comments
            params = {
                'query': query,
                'tags': 'story',  # Only get stories (not comments)
                'hitsPerPage': max_results
                # Note: Removed numericFilters to get more results
                # Can filter on client-side if needed
            }

            response = requests.get(
                f"{self.base_url}/search",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()

            if not data.get('hits'):
                print(f"No hits in response. Response keys: {data.keys()}")
                print(f"Full response: {data}")

            stories = []
            for hit in data.get('hits', []):
                story_id = hit.get('objectID')
                if not story_id:
                    continue

                # Fetch comments for this story
                comments = self._fetch_comments(story_id, hit.get('num_comments', 0))

                # Convert to Reddit-compatible format
                # Try different text fields in order of preference
                selftext = (hit.get('story_text') or
                           hit.get('text') or
                           hit.get('comment_text') or
                           '')

                stories.append({
                    'title': hit.get('title', ''),
                    'selftext': selftext,
                    'url': hit.get('url', f"https://news.ycombinator.com/item?id={story_id}"),
                    'subreddit': 'HackerNews',  # Unified field
                    'score': hit.get('points', 0),
                    'num_comments': hit.get('num_comments', 0),
                    'created_utc': self._parse_date(hit.get('created_at', '')),
                    'comments': comments,
                    'author': hit.get('author', 'unknown')
                })

            return stories

        except Exception as e:
            print(f"Error searching Hacker News: {str(e)}")
            return []

    def _fetch_comments(self, story_id: str, total_comments: int, max_comments: int = 30) -> List[Dict]:
        """
        Fetch top-level comments for a story.
        Note: Using search_by_date for comments as items API can be unreliable.
        """
        if total_comments == 0:
            return []

        try:
            # Search for comments on this story using search_by_date
            # This is more reliable than the items API
            response = requests.get(
                f"{self.base_url}/search",
                params={
                    'tags': f'comment,story_{story_id}',
                    'hitsPerPage': max_comments
                },
                timeout=10
            )
            response.raise_for_status()
            data = response.json()

            comments = []
            hits = data.get('hits', [])

            for hit in hits:
                try:
                    # Get comment text - try different field names
                    comment_text = (hit.get('comment_text') or
                                  hit.get('text') or
                                  hit.get('story_text') or
                                  '')

                    # Skip if no text or too short
                    if not isinstance(comment_text, str) or len(comment_text) < 20:
                        continue

                    comments.append({
                        'body': self._clean_html(comment_text),
                        'score': hit.get('points', 0),
                        'author': hit.get('author', 'unknown')
                    })
                except Exception as e:
                    # Skip problematic comments silently
                    continue

            return comments

        except Exception as e:
            print(f"Error fetching comments for story {story_id}: {str(e)}")
            return []

    def _clean_html(self, text: str) -> str:
        """
        Remove HTML tags from comment text.
        """
        import re
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        # Decode common HTML entities
        text = text.replace('&gt;', '>').replace('&lt;', '<').replace('&amp;', '&')
        text = text.replace('&#x27;', "'").replace('&quot;', '"')
        return text.strip()

    def _parse_date(self, date_str: str) -> int:
        """
        Parse ISO date string to Unix timestamp.
        """
        try:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return int(dt.timestamp())
        except:
            return 0
