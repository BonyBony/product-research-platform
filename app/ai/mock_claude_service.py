from typing import List, Dict
from app.models.research import PainPoint, SeverityLevel


class MockClaudeService:
    """
    Mock Claude service for demo/testing purposes.
    Returns pre-generated pain points without requiring Anthropic API access.
    """

    def extract_pain_points(
        self,
        reddit_posts: List[Dict],
        problem_statement: str,
        target_users: str
    ) -> List[PainPoint]:
        """
        Return mock pain points based on the Reddit data.
        Simulates what Claude AI would extract.
        """
        if not reddit_posts:
            return []

        # Generate realistic pain points based on the mock Reddit data
        pain_points = []

        # Extract from the first few posts
        for post in reddit_posts[:3]:
            # Create pain point from post
            if post.get('comments') and len(post['comments']) > 0:
                first_comment = post['comments'][0]

                # Determine severity based on engagement score
                severity = self._determine_severity(first_comment.get('score', 0))

                # Create description from post title and comment
                description = self._generate_description(post['title'], first_comment['text'])

                pain_point = PainPoint(
                    description=description,
                    quote=first_comment['text'][:200],  # Limit quote length
                    severity=severity,
                    source_url=post['url'],
                    frequency=1
                )
                pain_points.append(pain_point)

        # Add some specific pain points based on common themes in the mock data
        if len(pain_points) < 5 and len(reddit_posts) > 0:
            pain_points.extend(self._get_additional_pain_points(reddit_posts))

        # Sort pain points by:
        # 1. Frequency (descending) - most frequent pain points first
        # 2. Severity (High > Medium > Low)
        # 3. Keep only top 10
        severity_order = {SeverityLevel.HIGH: 3, SeverityLevel.MEDIUM: 2, SeverityLevel.LOW: 1}
        pain_points.sort(
            key=lambda p: (p.frequency, severity_order[p.severity]),
            reverse=True
        )

        return pain_points[:10]  # Limit to 10 pain points

    def _determine_severity(self, score: int) -> SeverityLevel:
        """
        Determine severity based on comment score (engagement).
        """
        if score > 100:
            return SeverityLevel.HIGH
        elif score > 50:
            return SeverityLevel.MEDIUM
        else:
            return SeverityLevel.LOW

    def _generate_description(self, title: str, comment: str) -> str:
        """
        Generate a clear description from title and comment.
        """
        # Simple extraction - take first sentence of comment or title
        if '.' in comment[:100]:
            return comment[:comment.find('.') + 1]
        elif len(title) < 80:
            return title
        else:
            return comment[:100] + "..."

    def _get_additional_pain_points(self, reddit_posts: List[Dict]) -> List[PainPoint]:
        """
        Generate additional pain points from common themes.
        """
        additional = []

        # Check if there are meal planning related posts
        keywords = " ".join([p.get('title', '') + " " + p.get('selftext', '') for p in reddit_posts]).lower()

        if any(word in keywords for word in ['meal', 'food', 'lunch', 'cooking']):
            additional = [
                PainPoint(
                    description="Lack of meal planning leads to unhealthy food choices and expensive takeout orders",
                    quote="I never know what to make and by the time lunch rolls around I'm too hungry to think. So I just grab whatever is easiest, which is usually junk food or expensive delivery.",
                    severity=SeverityLevel.HIGH,
                    source_url=reddit_posts[0]['url'],
                    frequency=3
                ),
                PainPoint(
                    description="Decision fatigue from having to plan every meal while working from home",
                    quote="The mental load of deciding what to eat three times a day on top of work is exhausting. I never realized how much cognitive energy goes into meal planning.",
                    severity=SeverityLevel.MEDIUM,
                    source_url=reddit_posts[1]['url'] if len(reddit_posts) > 1 else reddit_posts[0]['url'],
                    frequency=2
                ),
                PainPoint(
                    description="Food waste from buying groceries without proper planning or recipes",
                    quote="I waste so much food because I buy groceries with good intentions but then don't use them. Vegetables go bad before I get around to cooking them.",
                    severity=SeverityLevel.MEDIUM,
                    source_url=reddit_posts[2]['url'] if len(reddit_posts) > 2 else reddit_posts[0]['url'],
                    frequency=2
                )
            ]

        return additional
