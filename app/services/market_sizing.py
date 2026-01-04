"""
Market Size Estimation Engine
Estimates reach and market size for Indian consumer products
"""

from typing import Dict, Optional, Tuple
import re


class MarketSizingEngine:
    """
    Estimates market size and reach for Indian consumer products.
    Uses TAM/SAM/SOM framework with 2025 market data.
    """

    # Indian market data (2025)
    INDIA_INTERNET_USERS = 900_000_000  # 900M internet users
    INDIA_SMARTPHONE_USERS = 931_000_000  # 931M smartphone users
    INDIA_POPULATION = 1_450_000_000  # 1.45B total population

    # Market size data by category (USD)
    MARKET_DATA = {
        "cab_booking": {
            "market_size_usd": 22_250_000_000,  # $22.25B
            "growth_rate": "7.89% CAGR",
            "active_users": 50_000_000,  # 50M monthly active riders
            "tam_description": "India Taxi Market",
            "sources": ["Mordor Intelligence India Taxi Market Report 2025"]
        },
        "qcommerce": {
            "market_size_usd": 5_380_000_000,  # $5.38B (moderate estimate)
            "growth_rate": "16.07% CAGR",
            "active_users": 25_000_000,  # Estimated
            "tam_description": "India Quick Commerce Market",
            "sources": ["Market Research Reports 2025"]
        },
        "ecommerce": {
            "market_size_usd": 85_000_000_000,  # $85B
            "growth_rate": "18% CAGR",
            "active_users": 200_000_000,
            "tam_description": "India E-commerce Market",
            "sources": ["Industry Reports 2025"]
        },
        "fintech": {
            "market_size_usd": 150_000_000_000,  # $150B
            "growth_rate": "22% CAGR",
            "active_users": 300_000_000,
            "tam_description": "India Fintech Market",
            "sources": ["Fintech Market Analysis 2025"]
        },
        "food_delivery": {
            "market_size_usd": 15_000_000_000,  # $15B
            "growth_rate": "25% CAGR",
            "active_users": 80_000_000,
            "tam_description": "India Food Delivery Market",
            "sources": ["Food Tech Market Reports 2025"]
        },
        "developer_tools": {
            "market_size_usd": 5_000_000_000,  # $5B (India)
            "growth_rate": "20% CAGR",
            "active_users": 5_000_000,  # Developers in India
            "tam_description": "India Developer Tools Market",
            "sources": ["Tech Industry Reports 2025"]
        },
        "default": {
            "market_size_usd": 10_000_000_000,  # $10B default
            "growth_rate": "15% CAGR",
            "active_users": 50_000_000,
            "tam_description": "Indian Consumer Market",
            "sources": ["Market Estimates"]
        }
    }

    def __init__(self):
        self.category_keywords = {
            "cab_booking": ["cab", "taxi", "uber", "ola", "rapido", "ride", "booking", "transport"],
            "qcommerce": ["qcommerce", "quick commerce", "grocery", "zepto", "blinkit", "instamart", "delivery", "instant"],
            "ecommerce": ["ecommerce", "shopping", "online shopping", "amazon", "flipkart", "meesho"],
            "fintech": ["payment", "wallet", "upi", "banking", "loan", "credit", "paytm", "phonepe"],
            "food_delivery": ["food delivery", "swiggy", "zomato", "restaurant", "order food"],
            "developer_tools": ["api", "developer", "coding", "programming", "kubernetes", "deployment", "devops", "cloud"]
        }

    def identify_market_category(self, problem_statement: str, target_users: str) -> str:
        """
        Identify market category based on keywords in problem statement.
        """
        text = f"{problem_statement} {target_users}".lower()

        # Check each category
        for category, keywords in self.category_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    return category

        return "default"

    def estimate_reach(
        self,
        problem_statement: str,
        target_users: str,
        frequency: int,
        num_comments: int,
        severity: str
    ) -> Tuple[int, str]:
        """
        Estimate number of users affected by this pain point.

        Returns:
            Tuple of (reach_number, justification_text)
        """
        category = self.identify_market_category(problem_statement, target_users)
        market = self.MARKET_DATA.get(category, self.MARKET_DATA["default"])

        base_users = market["active_users"]

        # Calculate penetration rate based on evidence
        penetration_rate = self._calculate_penetration_rate(
            frequency=frequency,
            num_comments=num_comments,
            severity=severity
        )

        reach = int(base_users * penetration_rate)

        # Build justification
        justification = self._build_reach_justification(
            category=category,
            base_users=base_users,
            penetration_rate=penetration_rate,
            reach=reach,
            frequency=frequency,
            num_comments=num_comments,
            severity=severity
        )

        return reach, justification

    def _calculate_penetration_rate(
        self,
        frequency: int,
        num_comments: int,
        severity: str
    ) -> float:
        """
        Calculate what percentage of market is affected.

        Based on:
        - Frequency (how many times mentioned)
        - Number of comments/discussions
        - Severity level
        """
        # Base rate from frequency
        if frequency >= 10:
            base_rate = 0.40  # 40% of users
        elif frequency >= 5:
            base_rate = 0.30  # 30%
        elif frequency >= 3:
            base_rate = 0.20  # 20%
        else:
            base_rate = 0.10  # 10%

        # Adjust for number of comments (data quality)
        if num_comments >= 100:
            comment_multiplier = 1.2
        elif num_comments >= 50:
            comment_multiplier = 1.1
        elif num_comments >= 20:
            comment_multiplier = 1.0
        else:
            comment_multiplier = 0.8

        # Adjust for severity
        severity_multiplier = {
            "High": 1.2,
            "Medium": 1.0,
            "Low": 0.7
        }.get(severity, 1.0)

        # Calculate final rate
        penetration = base_rate * comment_multiplier * severity_multiplier

        # Cap at reasonable maximum
        return min(penetration, 0.50)  # Max 50% of market

    def _build_reach_justification(
        self,
        category: str,
        base_users: int,
        penetration_rate: float,
        reach: int,
        frequency: int,
        num_comments: int,
        severity: str
    ) -> str:
        """
        Build human-readable justification for reach estimate.
        """
        market = self.MARKET_DATA.get(category, self.MARKET_DATA["default"])

        justification = f"""**Reach Calculation:**
- Market: {market['tam_description']}
- Total Active Users: {base_users:,}
- Estimated Penetration: {penetration_rate*100:.0f}%

**Evidence:**
- Mentioned {frequency}x in user research
- {num_comments} comments/discussions analyzed
- Severity: {severity}

**Calculation:**
{base_users:,} users × {penetration_rate*100:.0f}% = {reach:,} affected users

**Source:** {', '.join(market['sources'])}"""

        return justification

    def get_market_data(
        self,
        problem_statement: str,
        target_users: str
    ) -> Dict:
        """
        Get full market data for a problem.
        """
        category = self.identify_market_category(problem_statement, target_users)
        market = self.MARKET_DATA.get(category, self.MARKET_DATA["default"])

        return {
            "category": category,
            "tam": market["tam_description"],
            "sam": f"{market['active_users']:,} active users in India",
            "som": "To be calculated based on pain point penetration",
            "market_size_usd": market["market_size_usd"],
            "growth_rate": market["growth_rate"],
            "sources": market["sources"]
        }
