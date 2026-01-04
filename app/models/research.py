from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class SeverityLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class DataSource(str, Enum):
    AUTO = "auto"  # Automatically select based on available API keys
    YOUTUBE = "youtube"
    REDDIT = "reddit"
    HACKERNEWS = "hackernews"
    PRODUCTHUNT = "producthunt"
    DEMO = "demo"


class ResearchRequest(BaseModel):
    problem_statement: str = Field(
        ...,
        description="The problem or domain to research",
        min_length=10,
        example="People struggle to find healthy meal options when working from home"
    )
    target_users: str = Field(
        ...,
        description="The target user segment",
        min_length=3,
        example="Remote workers"
    )
    source: Optional[DataSource] = Field(
        default=DataSource.AUTO,
        description="Data source to use (auto, youtube, reddit, hackernews, producthunt, demo)"
    )


class PainPoint(BaseModel):
    description: str = Field(
        ...,
        description="Clear description of the problem"
    )
    quote: str = Field(
        ...,
        description="Exact user quote from Reddit"
    )
    severity: SeverityLevel = Field(
        ...,
        description="Severity level of the pain point"
    )
    source_url: str = Field(
        ...,
        description="Reddit post URL"
    )
    frequency: int = Field(
        default=1,
        description="How often this pain point appeared",
        ge=1
    )


class ResearchResponse(BaseModel):
    pain_points: List[PainPoint] = Field(
        default_factory=list,
        description="List of extracted pain points"
    )
    total_posts_analyzed: int = Field(
        default=0,
        description="Number of Reddit posts analyzed"
    )
    total_comments_analyzed: int = Field(
        default=0,
        description="Number of comments analyzed"
    )
