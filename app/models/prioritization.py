from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from enum import Enum


class OpportunityCategory(str, Enum):
    UNDERSERVED = "underserved"
    OVERSERVED = "overserved"
    WELLSERVED = "wellserved"


class ImpactLevel(float, Enum):
    MINIMAL = 0.25
    LOW = 0.5
    MEDIUM = 1.0
    HIGH = 2.0
    MASSIVE = 3.0


class JTBDScore(BaseModel):
    """Jobs-to-be-Done opportunity scoring"""
    job_statement: str = Field(..., description="The job the user is trying to accomplish")
    importance: float = Field(..., description="How important is this job (0-10)", ge=0, le=10)
    satisfaction: float = Field(..., description="Current satisfaction level (0-10)", ge=0, le=10)
    opportunity_score: float = Field(..., description="Calculated opportunity score (0-20)")
    category: OpportunityCategory = Field(..., description="Under/Over/Well served category")
    reasoning: str = Field(..., description="Why this score was assigned")


class RICEScore(BaseModel):
    """RICE prioritization scoring"""
    reach: int = Field(..., description="Number of users affected", ge=0)
    reach_justification: str = Field(..., description="How reach was calculated")

    impact: float = Field(..., description="Impact multiplier (0.25-3.0)")
    impact_reasoning: str = Field(..., description="Why this impact level")

    confidence: float = Field(..., description="Confidence percentage (0-1)", ge=0, le=1)
    confidence_basis: str = Field(..., description="What data supports this confidence")

    effort: float = Field(..., description="Effort in person-months", gt=0)
    effort_breakdown: Dict[str, float] = Field(..., description="Breakdown of effort by component")

    rice_score: float = Field(..., description="Calculated RICE score")


class PersonaAlignment(BaseModel):
    """How pain point aligns with personas"""
    affected_personas: List[str] = Field(..., description="Names of affected personas")
    coverage: float = Field(..., description="Percentage of personas affected (0-1)", ge=0, le=1)
    affinities: Dict[str, str] = Field(..., description="Affinity level per persona (HIGH/MEDIUM/LOW)")
    weight: float = Field(..., description="Weighted alignment score")


class MarketData(BaseModel):
    """Market size and validation data"""
    tam: Optional[str] = Field(None, description="Total Addressable Market")
    sam: Optional[str] = Field(None, description="Serviceable Available Market")
    som: Optional[str] = Field(None, description="Serviceable Obtainable Market")
    market_size_usd: Optional[float] = Field(None, description="Market size in USD")
    growth_rate: Optional[str] = Field(None, description="CAGR or growth rate")
    market_gap: Optional[str] = Field(None, description="Description of market gap")
    sources: List[str] = Field(default_factory=list, description="Data sources")


class Justification(BaseModel):
    """Evidence-based justification for prioritization"""
    why_top_priority: str = Field(..., description="Main reason for this ranking")
    evidence: List[str] = Field(..., description="Supporting evidence points")
    market_data: Optional[MarketData] = Field(None, description="Market validation")
    quote_samples: List[str] = Field(default_factory=list, description="Representative user quotes")


class PrioritizedPainPoint(BaseModel):
    """A pain point with complete prioritization analysis"""
    pain_point_id: str = Field(..., description="Reference to original pain point")
    description: str = Field(..., description="Pain point description")
    original_severity: str = Field(..., description="Original severity from research")

    priority_rank: int = Field(..., description="Final priority ranking (1 = highest)")
    final_score: float = Field(..., description="Combined final score (0-200)")

    jtbd: JTBDScore = Field(..., description="JTBD opportunity analysis")
    rice: RICEScore = Field(..., description="RICE scoring breakdown")
    persona_alignment: PersonaAlignment = Field(..., description="Persona alignment analysis")
    justification: Justification = Field(..., description="Evidence-based justification")


class PrioritizationRequest(BaseModel):
    """Request to prioritize pain points"""
    pain_points: List[dict] = Field(..., description="Pain points from research")
    personas: List[dict] = Field(..., description="Generated personas")
    problem_statement: str = Field(..., description="Original problem statement")
    target_users: str = Field(..., description="Target user segment")
    market_context: Optional[Dict] = Field(
        default_factory=dict,
        description="Additional market context (geography, category, etc.)"
    )


class PrioritizationResponse(BaseModel):
    """Response with prioritized pain points"""
    prioritized_pain_points: List[PrioritizedPainPoint] = Field(
        ...,
        description="Pain points ranked by priority"
    )
    total_analyzed: int = Field(..., description="Number of pain points analyzed")
    top_opportunity: str = Field(..., description="Summary of top opportunity")
    methodology: str = Field(
        default="JTBD + RICE Hybrid (40% JTBD + 40% RICE + 20% Persona Alignment)",
        description="Methodology used for prioritization"
    )
