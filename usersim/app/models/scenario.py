from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from enum import Enum


class StepType(str, Enum):
    ACTION = "action"  # User takes an action
    SYSTEM_RESPONSE = "system_response"  # System responds
    DECISION_POINT = "decision_point"  # User must decide what to do
    ERROR = "error"  # Something goes wrong
    SUCCESS = "success"  # Goal achieved


class EmotionalState(str, Enum):
    NEUTRAL = "neutral"
    SATISFIED = "satisfied"
    HOPEFUL = "hopeful"
    FRUSTRATED = "frustrated"
    ANNOYED = "annoyed"
    ANGRY = "angry"
    DELIGHTED = "delighted"


class DecisionOption(BaseModel):
    """An option the user can choose"""
    option_id: str
    description: str  # e.g., "Retry same app", "Try alternative", "Give up"
    consequences: str  # What happens if chosen


class ChurnAnalysis(BaseModel):
    """Detailed churn probability analysis"""
    base_risk: float
    frustration_events: List[Dict]  # [{"event": "driver_cancel", "risk_added": 25}]
    formula_risk: float
    patience_multiplier: float
    calculated_risk: float
    ai_adjustments: List[Dict]  # [{"factor": "sunk_cost", "adjustment": -10}]
    final_churn_probability: float
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    reasoning: str


class JourneyStep(BaseModel):
    """A single step in the user journey"""
    step_number: int
    step_type: StepType
    description: str  # What happens in this step
    user_action: Optional[str] = None  # What user does (if ACTION type)
    system_response: Optional[str] = None  # How system responds

    # Emotional & behavioral tracking
    emotional_state: EmotionalState
    frustration_level: float = Field(..., ge=0, le=10, description="0-10 scale")

    # Churn analysis
    churn_analysis: Optional[ChurnAnalysis] = None

    # Decision point (if applicable)
    is_decision_point: bool = False
    decision_options: List[DecisionOption] = Field(default_factory=list)
    chosen_option: Optional[str] = None
    decision_reasoning: Optional[str] = None

    # Time tracking
    time_elapsed: float = Field(default=0, description="Cumulative time in seconds")
    step_duration: float = Field(default=0, description="Time spent on this step")


class ScenarioType(str, Enum):
    HAPPY_PATH = "happy_path"
    EDGE_CASE = "edge_case"
    FAILURE = "failure"


class Scenario(BaseModel):
    """A complete user journey scenario"""
    scenario_id: str
    scenario_name: str
    scenario_type: ScenarioType
    description: str  # What is this scenario testing?

    # The journey
    steps: List[JourneyStep]

    # Outcome
    outcome: str  # "Success", "User churned", "Partial success"
    final_churn_probability: float
    key_insights: List[str]  # Lessons from this scenario


class ScenarioRequest(BaseModel):
    """Request to generate scenarios for a problem"""
    problem_statement: str
    product_flow: str  # High-level description of how product should work
    user_profile_id: Optional[str] = None  # Use specific virtual user
    num_scenarios: int = Field(default=5, description="How many scenarios to generate")
    include_edge_cases: bool = Field(default=True)


class ScenarioSimulationResponse(BaseModel):
    """Complete simulation output"""
    virtual_user: Dict  # The user profile used
    scenarios: List[Scenario]
    summary_insights: List[str]  # Overall patterns across scenarios
    churn_hotspots: List[str]  # Steps where churn risk is highest
    recommendations: List[str]  # Product improvements to reduce churn
