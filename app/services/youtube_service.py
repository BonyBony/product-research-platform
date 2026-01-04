from googleapiclient.discovery import build
from typing import List, Dict
from datetime import datetime, timedelta
from app.config import get_settings


class YouTubeService:
    def __init__(self):
        settings = get_settings()
        self.youtube = build('youtube', 'v3', developerKey=settings.youtube_api_key)

    def search_posts(
        self,
        problem_statement: str,
        target_users: str,
        max_posts: int = 20,
        max_comments_per_post: int = 5,
        days_back: int = 365  # Increased to 1 year for better results
    ) -> List[Dict]:
        """
        Search YouTube for videos related to the problem statement.
        Returns list of videos with their top comments.
        """
        # Create focused search query using core keywords
        # Extract main topic - don't add generic context words that dilute the query
        core_keywords = self._extract_keywords(problem_statement, target_users)
        search_query = core_keywords  # Use keywords directly without additions

        # DEBUG: Print the search query
        print(f"\n{'='*60}")
        print(f"YOUTUBE SEARCH DEBUG")
        print(f"{'='*60}")
        print(f"Original Problem: {problem_statement}")
        print(f"Target Users: {target_users}")
        print(f"Extracted Keywords: {core_keywords}")
        print(f"Final Search Query: {search_query}")
        print(f"{'='*60}\n")

        results = []

        try:
            # Search for videos - minimal filters for best results
            # Don't use publishedAfter - good content might be older
            search_request = self.youtube.search().list(
                q=search_query,
                part='id,snippet',
                type='video',
                maxResults=min(max_posts, 50),  # YouTube API limit
                order='relevance',
                relevanceLanguage='en'
            )
            search_response = search_request.execute()

            # DEBUG: Print what we got back
            print(f"Videos found: {len(search_response.get('items', []))}")
            print(f"First few video titles:")
            for idx, item in enumerate(search_response.get('items', [])[:5]):
                print(f"  {idx+1}. {item['snippet']['title']}")
            print(f"{'='*60}\n")

            # Process each video
            for item in search_response.get('items', []):
                video_id = item['id']['videoId']
                snippet = item['snippet']

                # Get comments for this video
                comments = self._get_video_comments(video_id, max_comments_per_post)

                # Only include videos that have comments
                if comments:
                    results.append({
                        'title': snippet['title'],
                        'selftext': snippet['description'][:500] if snippet.get('description') else '',
                        'url': f"https://www.youtube.com/watch?v={video_id}",
                        'subreddit': snippet['channelTitle'],
                        'score': 0,  # YouTube doesn't have upvotes like Reddit
                        'num_comments': len(comments),
                        'created_utc': self._parse_youtube_date(snippet['publishedAt']),
                        'comments': comments
                    })

                # Stop if we have enough results
                if len(results) >= max_posts:
                    break

        except Exception as e:
            print(f"YouTube API Error: {str(e)}")
            return []

        return results

    def _get_video_comments(self, video_id: str, max_comments: int) -> List[Dict]:
        """
        Fetch top comments for a video.
        """
        comments = []

        try:
            comment_request = self.youtube.commentThreads().list(
                part='snippet',
                videoId=video_id,
                maxResults=max_comments,
                order='relevance',
                textFormat='plainText'
            )
            comment_response = comment_request.execute()

            for item in comment_response.get('items', []):
                top_comment = item['snippet']['topLevelComment']['snippet']

                # Filter out very short comments
                if len(top_comment['textDisplay']) > 20:
                    comments.append({
                        'text': top_comment['textDisplay'],
                        'score': top_comment.get('likeCount', 0),
                        'author': top_comment.get('authorDisplayName', 'Unknown')
                    })

        except Exception as e:
            # Video might have comments disabled
            print(f"Could not fetch comments for video {video_id}: {str(e)}")
            return []

        return comments

    def _parse_youtube_date(self, date_string: str) -> float:
        """
        Convert YouTube date string to Unix timestamp.
        """
        try:
            dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            return dt.timestamp()
        except:
            return datetime.utcnow().timestamp()

    def _extract_keywords(self, problem_statement: str, target_users: str) -> str:
        """
        Extract core keywords from problem statement for better YouTube search.
        Removes only common filler words, keeps domain-specific terms.
        """
        # Only remove truly generic filler words
        stop_words = {
            'i', 'want', 'to', 'understand', 'what', 'are', 'the', 'a', 'an',
            'and', 'or', 'but', 'in', 'on', 'at', 'is', 'was', 'were', 'be',
            'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'should', 'could', 'may', 'might', 'must', 'can', 'that',
            'this', 'these', 'those', 'it', 'its', 'of', 'as', 'by', 'for',
            'from', 'with', 'when', 'where', 'who', 'which', 'why', 'how'
        }

        # Combine and clean
        text = f"{problem_statement} {target_users}".lower()

        # Remove punctuation
        import string
        text = text.translate(str.maketrans('', '', string.punctuation))

        # Extract words, filter stop words
        words = [w for w in text.split() if w not in stop_words and len(w) > 2]

        # Keep more keywords (up to 10) to maintain context and domain specificity
        return ' '.join(words[:10])

    def get_relevant_subreddits(self, problem_statement: str, limit: int = 5) -> List[str]:
        """
        For compatibility with Reddit service interface.
        Returns empty list for YouTube.
        """
        return []
