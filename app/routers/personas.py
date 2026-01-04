from fastapi import APIRouter, HTTPException, status
from app.models.persona import PersonaGenerationRequest, PersonaGenerationResponse
from app.services.persona_service import PersonaService
from app.config import get_settings

router = APIRouter(
    prefix="/api",
    tags=["personas"]
)


@router.post("/personas", response_model=PersonaGenerationResponse, status_code=status.HTTP_200_OK)
async def generate_personas(request: PersonaGenerationRequest):
    """
    Generate user personas from research pain points.

    This endpoint:
    1. Takes pain points from the /api/research endpoint
    2. Uses Claude AI to analyze patterns and user segments
    3. Creates 2-5 realistic, diverse user personas
    4. Returns rich persona data for visualization

    Each persona includes:
    - Demographics (name, age, occupation, location)
    - Goals and motivations
    - Pain points and frustrations
    - Behaviors and usage patterns
    - Characteristic quote
    - Tech savviness and spending patterns

    Args:
        request: PersonaGenerationRequest with pain points and context

    Returns:
        PersonaGenerationResponse with generated personas
    """
    try:
        settings = get_settings()

        # Initialize persona service
        persona_service = PersonaService()

        # Generate personas
        personas = persona_service.generate_personas(
            pain_points=request.pain_points,
            problem_statement=request.problem_statement,
            target_users=request.target_users,
            num_personas=request.num_personas
        )

        if not personas:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate personas. Please check your pain points data."
            )

        return PersonaGenerationResponse(
            personas=personas,
            total_personas=len(personas),
            based_on_pain_points=len(request.pain_points)
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate personas: {str(e)}"
        )
