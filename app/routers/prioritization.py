from fastapi import APIRouter, HTTPException, status
from app.models.prioritization import PrioritizationRequest, PrioritizationResponse
from app.services.prioritization_service import PrioritizationService
from app.config import get_settings

router = APIRouter(
    prefix="/api",
    tags=["prioritization"]
)


@router.post("/prioritize", response_model=PrioritizationResponse, status_code=status.HTTP_200_OK)
async def prioritize_pain_points(request: PrioritizationRequest):
    """
    Prioritize pain points using JTBD + RICE hybrid framework.

    This endpoint:
    1. Analyzes pain points using Jobs-to-be-Done framework
    2. Calculates RICE scores (Reach, Impact, Confidence, Effort)
    3. Evaluates persona alignment
    4. Returns prioritized list with evidence-based justification

    **Methodology:**
    - 40% JTBD Opportunity Score (customer-centric discovery)
    - 40% RICE Score (data-driven quantification)
    - 20% Persona Alignment (strategic fit)

    **JTBD Components:**
    - Job Statement: What job is the user trying to accomplish?
    - Importance (0-10): How critical is this job?
    - Satisfaction (0-10): How well are current solutions working?
    - Opportunity Score: Importance + max(Importance - Satisfaction, 0)
    - Category: Underserved (>10), Wellserved (8-10), Overserved (<8)

    **RICE Components:**
    - Reach: Estimated users affected (market size research)
    - Impact: 0.25-3.0 multiplier based on severity and importance
    - Confidence: 0-100% based on data quality and consistency
    - Effort: Person-months to implement (AI-estimated)

    **Persona Alignment:**
    - Which personas are affected by this pain point
    - Affinity level (Very High, High, Medium, Low)
    - Coverage percentage

    Args:
        request: PrioritizationRequest with pain_points, personas, problem_statement, target_users

    Returns:
        PrioritizationResponse with prioritized pain points and full analysis
    """
    try:
        settings = get_settings()

        if not settings.anthropic_api_key:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Anthropic API key not configured. Prioritization requires Claude AI."
            )

        # Initialize prioritization service
        prioritization_service = PrioritizationService()

        # Prioritize pain points
        prioritized = prioritization_service.prioritize_pain_points(
            pain_points=request.pain_points,
            personas=request.personas,
            problem_statement=request.problem_statement,
            target_users=request.target_users,
            market_context=request.market_context
        )

        if not prioritized:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to prioritize pain points. Please check your input data."
            )

        # Build top opportunity summary
        top_pp = prioritized[0]
        top_opportunity = f"{top_pp.description} (Score: {top_pp.final_score}/200, JTBD: {top_pp.jtbd.opportunity_score}/20)"

        return PrioritizationResponse(
            prioritized_pain_points=prioritized,
            total_analyzed=len(prioritized),
            top_opportunity=top_opportunity,
            methodology="JTBD + RICE Hybrid (40% JTBD + 40% RICE + 20% Persona Alignment)"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to prioritize pain points: {str(e)}"
        )
