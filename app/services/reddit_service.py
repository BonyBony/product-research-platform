import praw
from typing import List, Dict
from datetime import datetime, timedelta
from app.config import get_settings


class RedditService:
    def __init__(self):
        settings = get_settings()
        self.reddit = praw.Reddit(
            client_id=settings.reddit_client_id,
            client_secret=settings.reddit_client_secret,
            user_agent=settings.reddit_user_agent
        )

    def search_posts(
        self,
        problem_statement: str,
        target_users: str,
        max_posts: int = 20,
        max_comments_per_post: int = 5,
        days_back: int = 30
    ) -> List[Dict]:
        """
        Search Reddit for posts related to the problem statement.
        Returns list of posts with their top comments.
        """
        search_query = f"{problem_statement} {target_users}"
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)

        results = []

        # Search across all of Reddit
        for submission in self.reddit.subreddit("all").search(
            search_query,
            sort="relevance",
            time_filter="month",
            limit=max_posts
        ):
            # Skip if post is too old
            post_date = datetime.utcfromtimestamp(submission.created_utc)
            if post_date < cutoff_date:
                continue

            # Get top comments
            submission.comment_sort = "top"
            submission.comments.replace_more(limit=0)
            top_comments = []

            for comment in submission.comments[:max_comments_per_post]:
                if hasattr(comment, 'body') and len(comment.body) > 20:
                    top_comments.append({
                        "text": comment.body,
                        "score": comment.score,
                        "author": str(comment.author) if comment.author else "[deleted]"
                    })

            results.append({
                "title": submission.title,
                "selftext": submission.selftext,
                "url": f"https://reddit.com{submission.permalink}",
                "subreddit": str(submission.subreddit),
                "score": submission.score,
                "num_comments": submission.num_comments,
                "created_utc": submission.created_utc,
                "comments": top_comments
            })

        return results

    def get_relevant_subreddits(self, problem_statement: str, limit: int = 5) -> List[str]:
        """
        Find relevant subreddits based on the problem statement.
        """
        subreddits = []

        try:
            for subreddit in self.reddit.subreddits.search(problem_statement, limit=limit):
                subreddits.append(subreddit.display_name)
        except Exception:
            pass

        return subreddits
