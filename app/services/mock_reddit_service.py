from typing import List, Dict
from datetime import datetime, timedelta
import random


class MockRedditService:
    """
    Mock Reddit service for demo/testing purposes.
    Returns realistic sample data without requiring Reddit API access.
    """

    def __init__(self):
        self.mock_data = self._generate_mock_data()

    def search_posts(
        self,
        problem_statement: str,
        target_users: str,
        max_posts: int = 20,
        max_comments_per_post: int = 5,
        days_back: int = 30
    ) -> List[Dict]:
        """
        Return mock Reddit posts with realistic data.
        """
        # Filter and return relevant mock posts
        relevant_posts = []

        # Determine which dataset to use based on keywords
        keywords = (problem_statement + " " + target_users).lower()

        if any(word in keywords for word in ["meal", "food", "healthy", "eat", "cooking", "remote"]):
            relevant_posts = self._get_meal_planning_posts()
        elif any(word in keywords for word in ["fitness", "workout", "exercise", "gym"]):
            relevant_posts = self._get_fitness_posts()
        elif any(word in keywords for word in ["productivity", "work", "focus", "distraction"]):
            relevant_posts = self._get_productivity_posts()
        else:
            # Default to meal planning
            relevant_posts = self._get_meal_planning_posts()

        # Limit to requested number of posts
        return relevant_posts[:max_posts]

    def get_relevant_subreddits(self, problem_statement: str, limit: int = 5) -> List[str]:
        """
        Return mock relevant subreddits.
        """
        return ["WorkFromHome", "productivity", "HealthyFood", "MealPrep", "remote"]

    def _generate_mock_data(self) -> Dict:
        """
        Generate mock data sets for different problem domains.
        """
        return {
            "meal_planning": self._get_meal_planning_posts(),
            "fitness": self._get_fitness_posts(),
            "productivity": self._get_productivity_posts()
        }

    def _get_meal_planning_posts(self) -> List[Dict]:
        """
        Mock posts about meal planning for remote workers.
        """
        base_time = datetime.utcnow().timestamp()

        return [
            {
                "title": "Struggling with lunch options while WFH",
                "selftext": "I've been working from home for 6 months now and I still can't figure out what to eat for lunch. I end up ordering takeout almost every day which is expensive and unhealthy. Anyone else dealing with this?",
                "url": "https://reddit.com/r/WorkFromHome/mock/post1",
                "subreddit": "WorkFromHome",
                "score": 342,
                "num_comments": 87,
                "created_utc": base_time - (3 * 86400),
                "comments": [
                    {
                        "text": "Same here! I never know what to make and by the time lunch rolls around I'm too hungry to think. So I just grab whatever is easiest, which is usually junk food or expensive delivery.",
                        "score": 156,
                        "author": "user123"
                    },
                    {
                        "text": "The problem is meal planning takes too much mental energy. After working all morning I don't want to think about cooking. I wish there was an app that could just tell me what to make with what I have.",
                        "score": 98,
                        "author": "busyprofessional"
                    },
                    {
                        "text": "I spend more on food now than when I was going to the office. At least the office cafeteria was convenient and relatively healthy. Now I'm stuck between spending 30 mins cooking or $15 on delivery.",
                        "score": 67,
                        "author": "remoteworker99"
                    },
                    {
                        "text": "My biggest issue is that I don't have time to grocery shop properly. I never have the right ingredients on hand, so even if I want to cook something healthy, I can't.",
                        "score": 45,
                        "author": "healthyeater"
                    },
                    {
                        "text": "Anyone else just eating cereal or sandwiches every day? I know it's not ideal but I can't deal with the decision fatigue of choosing what to eat.",
                        "score": 34,
                        "author": "cereallover"
                    }
                ]
            },
            {
                "title": "Remote workers: How do you handle meal prep?",
                "selftext": "I'm curious how other remote workers manage their meals. Do you meal prep? Order out? Cook every meal? I feel like I'm spending way too much time thinking about food.",
                "url": "https://reddit.com/r/remote/mock/post2",
                "subreddit": "remote",
                "score": 234,
                "num_comments": 56,
                "created_utc": base_time - (7 * 86400),
                "comments": [
                    {
                        "text": "I tried meal prepping on Sundays but by Wednesday I'm sick of eating the same thing. Plus I don't have a big enough fridge to store everything.",
                        "score": 89,
                        "author": "mealprepper"
                    },
                    {
                        "text": "The transition from office to home was rough. I used to eat out with coworkers which gave structure. Now I'm snacking constantly throughout the day instead of proper meals.",
                        "score": 72,
                        "author": "officenostalgia"
                    },
                    {
                        "text": "I waste so much food because I buy groceries with good intentions but then don't use them. Vegetables go bad before I get around to cooking them.",
                        "score": 58,
                        "author": "foodwaster"
                    },
                    {
                        "text": "Honestly I just eat whatever is quick - yogurt, protein bars, instant noodles. I know it's not healthy but I don't have the energy to plan and cook proper meals while working full time.",
                        "score": 41,
                        "author": "quickeats"
                    }
                ]
            },
            {
                "title": "Anyone else's eating habits completely fall apart while WFH?",
                "selftext": "Before COVID I ate pretty healthy - packed lunch, balanced meals. Now I'm either forgetting to eat until 3pm or eating junk all day. What happened?",
                "url": "https://reddit.com/r/WorkFromHome/mock/post3",
                "subreddit": "WorkFromHome",
                "score": 478,
                "num_comments": 124,
                "created_utc": base_time - (5 * 86400),
                "comments": [
                    {
                        "text": "YES! I either skip meals completely because I'm in the zone working, or I'm constantly snacking. There's no in-between. The structure of office life helped regulate my eating.",
                        "score": 201,
                        "author": "snackattack"
                    },
                    {
                        "text": "I gained 15 pounds in the first year of WFH. The fridge is right there and I have no self control. Also cooking for one person is depressing so I order too much delivery.",
                        "score": 143,
                        "author": "covidweight"
                    },
                    {
                        "text": "The mental load of deciding what to eat three times a day on top of work is exhausting. I never realized how much cognitive energy goes into meal planning.",
                        "score": 98,
                        "author": "decisionfatigue"
                    },
                    {
                        "text": "I miss having coworkers to go to lunch with. Eating alone at home every day is isolating and makes me not want to put effort into meals.",
                        "score": 67,
                        "author": "lonelylunch"
                    },
                    {
                        "text": "The worst part is the guilt. I know I should be cooking healthy meals since I'm home, but I just can't get motivated to do it. Then I feel bad about ordering takeout again.",
                        "score": 54,
                        "author": "guiltyeater"
                    }
                ]
            },
            {
                "title": "Healthy lunch ideas for remote workers?",
                "selftext": "Looking for quick, healthy lunch options that don't require much preparation. I work from home and need something I can make in under 15 minutes.",
                "url": "https://reddit.com/r/HealthyFood/mock/post4",
                "subreddit": "HealthyFood",
                "score": 167,
                "num_comments": 43,
                "created_utc": base_time - (10 * 86400),
                "comments": [
                    {
                        "text": "I struggle with this too. Everything 'quick' is unhealthy and everything 'healthy' takes 45 minutes to prepare. There's no good middle ground for busy people.",
                        "score": 76,
                        "author": "busycooker"
                    },
                    {
                        "text": "Salads are the obvious answer but I get bored of them so quickly. Plus buying all the ingredients for a good salad ends up being expensive and wasteful if you live alone.",
                        "score": 54,
                        "author": "saladbored"
                    },
                    {
                        "text": "The issue is planning ahead. If I'm being honest, I never think about lunch until I'm already hungry, and then it's too late to make anything that requires prep.",
                        "score": 38,
                        "author": "hangryworker"
                    }
                ]
            },
            {
                "title": "WFH has destroyed my relationship with food",
                "selftext": "I used to enjoy cooking on weekends. Now that I'm home all the time, cooking feels like another chore. I'm burned out on deciding what to eat constantly.",
                "url": "https://reddit.com/r/WorkFromHome/mock/post5",
                "subreddit": "WorkFromHome",
                "score": 289,
                "num_comments": 67,
                "created_utc": base_time - (12 * 86400),
                "comments": [
                    {
                        "text": "SAME. Cooking used to be relaxing, now it's just another task on my to-do list. I have to plan breakfast, lunch, dinner, and snacks every single day. It's overwhelming.",
                        "score": 134,
                        "author": "cookingburnout"
                    },
                    {
                        "text": "Decision fatigue is real. By the time I finish work I've made 100 decisions. Choosing what to make for dinner feels impossible so I just order pizza again.",
                        "score": 89,
                        "author": "toodecided"
                    },
                    {
                        "text": "I never appreciated how much the office environment structured my day, including meals. Now everything blends together and food is just fuel, not enjoyment.",
                        "score": 56,
                        "author": "structurelost"
                    }
                ]
            }
        ]

    def _get_fitness_posts(self) -> List[Dict]:
        """
        Mock posts about fitness challenges.
        """
        base_time = datetime.utcnow().timestamp()

        return [
            {
                "title": "Can't stay consistent with workouts",
                "selftext": "I start strong but always lose motivation after 2 weeks. Anyone else struggle with this?",
                "url": "https://reddit.com/r/fitness/mock/post1",
                "subreddit": "fitness",
                "score": 456,
                "num_comments": 92,
                "created_utc": base_time - (4 * 86400),
                "comments": [
                    {
                        "text": "Same here. I think the problem is I go too hard at the start and burn out quickly.",
                        "score": 178,
                        "author": "fitnessfail"
                    },
                    {
                        "text": "Life gets in the way. Work stress, family obligations - there's always an excuse not to go.",
                        "score": 123,
                        "author": "busylife"
                    }
                ]
            }
        ]

    def _get_productivity_posts(self) -> List[Dict]:
        """
        Mock posts about productivity issues.
        """
        base_time = datetime.utcnow().timestamp()

        return [
            {
                "title": "Distractions are killing my productivity",
                "selftext": "I can't focus for more than 20 minutes before checking my phone or browsing reddit.",
                "url": "https://reddit.com/r/productivity/mock/post1",
                "subreddit": "productivity",
                "score": 567,
                "num_comments": 104,
                "created_utc": base_time - (6 * 86400),
                "comments": [
                    {
                        "text": "I have the same issue. Social media is designed to be addictive and I can't resist.",
                        "score": 234,
                        "author": "distracted"
                    },
                    {
                        "text": "Working from home made it worse. At least in the office there was some accountability.",
                        "score": 156,
                        "author": "wfhstruggle"
                    }
                ]
            }
        ]
