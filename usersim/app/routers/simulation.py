from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from app.config import get_settings
from app.ai.decision_engine import AIDecisionEngine
from app.services.scenario_simulator import ScenarioSimulator
from app.models.scenario import ScenarioSimulationResponse


router = APIRouter(prefix="/api", tags=["simulation"])


class SimulationRequest(BaseModel):
    problem_statement: str
    product_flow: str
    target_users: str
    num_scenarios: int = 5
    persona_data: Optional[Dict[str, Any]] = None  # Import from ResearchAI


@router.post("/simulate", response_model=ScenarioSimulationResponse)
async def simulate_user_journey(request: SimulationRequest):
    """
    Generate virtual user and simulate scenarios

    This is the main endpoint that:
    1. Creates a virtual user from the problem statement
    2. Generates realistic scenarios (happy path + edge cases)
    3. Simulates user behavior with AI decision-making
    4. Calculates churn probability at each step
    5. Returns visual journey data
    """
    try:
        settings = get_settings()

        # Step 1: Generate virtual user
        decision_engine = AIDecisionEngine(settings.anthropic_api_key)
        virtual_user = decision_engine.generate_virtual_user(
            problem_statement=request.problem_statement,
            target_users=request.target_users,
            persona_data=request.persona_data  # Use imported persona if available
        )

        # Step 2: Generate and simulate scenarios
        simulator = ScenarioSimulator(settings.anthropic_api_key)
        result = simulator.generate_and_simulate_scenarios(
            problem_statement=request.problem_statement,
            product_flow=request.product_flow,
            virtual_user=virtual_user,
            num_scenarios=request.num_scenarios
        )

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
