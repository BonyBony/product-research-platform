import requests
from typing import List, Dict
import string
from datetime import datetime
from app.config import get_settings


class ProductHuntService:
    """
    Service to search Product Hunt for product discussions and reviews.
    Requires Product Hunt API token (get from: https://www.producthunt.com/v2/oauth/applications)

    Great for product feedback, feature requests, and competitive analysis.
    """

    def __init__(self):
        settings = get_settings()
        self.api_token = settings.producthunt_api_token if hasattr(settings, 'producthunt_api_token') else None
        self.base_url = "https://api.producthunt.com/v2/api/graphql"

    def search(self, problem_statement: str, target_users: str, max_results: int = 20) -> List[Dict]:
        """
        Search Product Hunt for posts and comments related to the problem.

        Args:
            problem_statement: The problem to research
            target_users: Target user segment
            max_results: Maximum number of posts to return

        Returns:
            List of posts with comments in Reddit-compatible format
        """
        if not self.api_token:
            print("\nWARNING: Product Hunt API token not configured.")
            print("To use Product Hunt integration:")
            print("1. Create an app at https://www.producthunt.com/v2/oauth/applications")
            print("2. Add PRODUCTHUNT_API_TOKEN to your .env file")
            print("3. Restart the server\n")
            return []

        keywords = self._extract_keywords(problem_statement, target_users)

        print("\n" + "=" * 60)
        print("PRODUCT HUNT SEARCH DEBUG")
        print("=" * 60)
        print(f"Original Problem: {problem_statement}")
        print(f"Target Users: {target_users}")
        print(f"Extracted Keywords: {keywords}")
        print("=" * 60)

        posts = self._search_posts(keywords, max_results)

        print(f"\nPosts found: {len(posts)}")
        if posts:
            print("First few post titles:")
            for idx, post in enumerate(posts[:5], 1):
                print(f"  {idx}. {post['title']}")
        print("=" * 60 + "\n")

        return posts

    def _extract_keywords(self, problem_statement: str, target_users: str) -> str:
        """
        Extract relevant keywords from problem statement and target users.
        """
        stop_words = {
            'i', 'want', 'to', 'understand', 'what', 'are', 'the', 'a', 'an',
            'and', 'or', 'but', 'in', 'on', 'at', 'is', 'was', 'were', 'be',
            'of', 'for', 'with', 'as', 'by', 'this', 'that', 'from', 'have',
            'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'
        }

        text = f"{problem_statement} {target_users}".lower()
        text = text.translate(str.maketrans('', '', string.punctuation))
        words = [w for w in text.split() if w not in stop_words and len(w) > 2]

        return ' '.join(words[:10])

    def _search_posts(self, query: str, max_results: int) -> List[Dict]:
        """
        Search for posts on Product Hunt using GraphQL API.
        """
        try:
            # GraphQL query to search posts
            graphql_query = """
            query SearchPosts($query: String!, $first: Int!) {
                posts(first: $first, order: VOTES, searchQuery: $query) {
                    edges {
                        node {
                            id
                            name
                            tagline
                            description
                            votesCount
                            commentsCount
                            createdAt
                            url
                            website
                            user {
                                name
                            }
                            comments(first: 20) {
                                edges {
                                    node {
                                        body
                                        votesCount
                                        user {
                                            name
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
            """

            headers = {
                'Authorization': f'Bearer {self.api_token}',
                'Content-Type': 'application/json'
            }

            response = requests.post(
                self.base_url,
                json={
                    'query': graphql_query,
                    'variables': {
                        'query': query,
                        'first': max_results
                    }
                },
                headers=headers,
                timeout=15
            )
            response.raise_for_status()
            data = response.json()

            if 'errors' in data:
                print(f"GraphQL errors: {data['errors']}")
                return []

            posts = []
            edges = data.get('data', {}).get('posts', {}).get('edges', [])

            for edge in edges:
                node = edge.get('node', {})

                # Extract comments
                comments = []
                comment_edges = node.get('comments', {}).get('edges', [])
                for comment_edge in comment_edges:
                    comment_node = comment_edge.get('node', {})
                    if comment_node.get('body'):
                        comments.append({
                            'body': comment_node.get('body', ''),
                            'score': comment_node.get('votesCount', 0),
                            'author': comment_node.get('user', {}).get('name', 'unknown')
                        })

                # Convert to Reddit-compatible format
                posts.append({
                    'title': node.get('name', ''),
                    'selftext': f"{node.get('tagline', '')}. {node.get('description', '')}",
                    'url': node.get('url', node.get('website', '')),
                    'subreddit': 'ProductHunt',
                    'score': node.get('votesCount', 0),
                    'num_comments': node.get('commentsCount', 0),
                    'created_utc': self._parse_date(node.get('createdAt')),
                    'comments': comments,
                    'author': node.get('user', {}).get('name', 'unknown')
                })

            return posts

        except Exception as e:
            print(f"Error searching Product Hunt: {str(e)}")
            return []

    def _parse_date(self, date_str: str) -> int:
        """
        Parse ISO date string to Unix timestamp.
        """
        try:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return int(dt.timestamp())
        except:
            return 0
