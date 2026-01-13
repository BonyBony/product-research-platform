from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from enum import Enum


class PatienceLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class SensitivityAttribute(BaseModel):
    """Generic sensitivity attribute (price, time, quality, etc.)"""
    name: str  # e.g., "price_sensitivity", "time_sensitivity"
    level: float = Field(..., ge=0, le=10, description="0-10 scale")
    description: str  # e.g., "Highly price-conscious, will wait for deals"


class BehavioralTrait(BaseModel):
    """Generic behavioral trait"""
    name: str  # e.g., "tech_savvy", "patience", "brand_loyalty"
    value: float = Field(..., ge=0, le=10, description="0-10 scale")
    description: str


class FrustrationTrigger(BaseModel):
    """What frustrates this user"""
    trigger: str  # e.g., "wait_time_exceeded", "price_increase", "feature_unavailable"
    threshold: float  # At what point does this trigger? (e.g., 5 mins for wait time)
    impact: float = Field(..., ge=0, le=100, description="How much churn risk does this add?")


class VirtualUser(BaseModel):
    """Generic virtual user profile - works for any domain"""
    name: str
    age: int
    occupation: str
    location: str

    # Problem-specific context
    problem_context: str  # e.g., "Daily commuter looking for cab booking solution"
    primary_goal: str  # e.g., "Save money on daily commute"

    # Behavioral attributes (generic, customizable per problem)
    sensitivities: List[SensitivityAttribute] = Field(
        default_factory=list,
        description="What this user cares about (price, time, quality, etc.)"
    )

    traits: List[BehavioralTrait] = Field(
        default_factory=list,
        description="Behavioral characteristics"
    )

    patience_level: PatienceLevel
    patience_multiplier: float = Field(
        default=1.5,
        description="How patience affects churn (low=2.0x, medium=1.5x, high=1.0x)"
    )

    # Frustration triggers
    frustration_triggers: List[FrustrationTrigger] = Field(
        default_factory=list,
        description="What causes this user to churn"
    )

    # Current state
    base_churn_risk: float = Field(default=10.0, description="Baseline churn probability")

    # Optional: Import from ResearchAI persona
    persona_source: Optional[str] = None  # Link to original persona if imported


class UserProfileRequest(BaseModel):
    """Request to create virtual user from problem statement"""
    problem_statement: str
    target_users: str
    persona_data: Optional[Dict] = None  # Optional: Import from ResearchAI
