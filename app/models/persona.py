from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class TechSavviness(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class Persona(BaseModel):
    name: str = Field(..., description="Full name of the persona")
    age: int = Field(..., description="Age of the persona", ge=18, le=80)
    occupation: str = Field(..., description="Job title or occupation")
    location: str = Field(..., description="City and country")
    background: str = Field(..., description="Brief background and lifestyle context")
    image_description: str = Field(..., description="Description for generating persona image")

    goals: List[str] = Field(..., description="What they want to achieve", min_items=2, max_items=5)
    pain_points: List[str] = Field(..., description="Their frustrations and problems", min_items=2, max_items=6)
    behaviors: List[str] = Field(..., description="How they act and what they do", min_items=2, max_items=5)

    quote: str = Field(..., description="A characteristic quote from this persona")

    tech_savviness: TechSavviness = Field(..., description="How tech-savvy they are")
    shopping_frequency: Optional[str] = Field(None, description="How often they shop/use the product")
    avg_spend: Optional[str] = Field(None, description="Average spending or usage")

    motivations: List[str] = Field(default_factory=list, description="What drives them", max_items=3)
    frustrations: List[str] = Field(default_factory=list, description="What blocks them", max_items=3)


class PersonaGenerationRequest(BaseModel):
    pain_points: List[dict] = Field(..., description="Pain points from research")
    problem_statement: str = Field(..., description="Original problem statement")
    target_users: str = Field(..., description="Target user segment")
    num_personas: int = Field(default=3, description="Number of personas to generate", ge=2, le=5)


class PersonaGenerationResponse(BaseModel):
    personas: List[Persona] = Field(..., description="Generated user personas")
    total_personas: int = Field(..., description="Number of personas generated")
    based_on_pain_points: int = Field(..., description="Number of pain points analyzed")
