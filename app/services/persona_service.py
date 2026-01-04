from anthropic import Anthropic
from typing import List, Dict
import json
from app.config import get_settings
from app.models.persona import Persona, TechSavviness


class PersonaService:
    def __init__(self):
        settings = get_settings()
        self.client = Anthropic(api_key=settings.anthropic_api_key)
        self.model = "claude-sonnet-4-5"

    def generate_personas(
        self,
        pain_points: List[Dict],
        problem_statement: str,
        target_users: str,
        num_personas: int = 3
    ) -> List[Persona]:
        """
        Generate user personas based on pain points using Claude AI.
        """
        if not pain_points:
            return []

        # Prepare pain points context
        pain_points_text = self._format_pain_points(pain_points)

        # Create the prompt
        prompt = self._create_persona_prompt(
            pain_points_text,
            problem_statement,
            target_users,
            num_personas
        )

        # Call Claude API
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4000,
            temperature=0.7,  # Higher temperature for creative persona generation
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        # Parse the response
        personas = self._parse_response(response.content[0].text)

        return personas[:num_personas]  # Ensure we don't exceed requested number

    def _format_pain_points(self, pain_points: List[Dict]) -> str:
        """
        Format pain points into readable text for Claude.
        """
        formatted = []
        for idx, pp in enumerate(pain_points, 1):
            formatted.append(f"{idx}. {pp.get('description', '')}")
            formatted.append(f"   Quote: \"{pp.get('quote', '')}\"")
            formatted.append(f"   Severity: {pp.get('severity', 'Medium')}")
            formatted.append("")

        return "\n".join(formatted)

    def _create_persona_prompt(
        self,
        pain_points_text: str,
        problem_statement: str,
        target_users: str,
        num_personas: int
    ) -> str:
        """
        Create the prompt for Claude to generate personas.
        """
        return f"""You are a UX researcher creating realistic user personas based on actual user pain points.

Problem Context:
{problem_statement}

Target Users:
{target_users}

Pain Points (from real user research):
{pain_points_text}

Your task:
Create {num_personas} distinct, realistic user personas that represent different segments of the target audience. Each persona should:
1. Have a realistic Indian name, age, occupation, and location
2. Reflect the pain points above in their behaviors and frustrations
3. Have unique characteristics, goals, and contexts
4. Feel like a real person, not a stereotype
5. Include specific, actionable details

IMPORTANT: Make personas diverse:
- Different ages (20s, 30s, 40s+)
- Different occupations (students, professionals, business owners, homemakers)
- Different tech savviness levels
- Different usage patterns and motivations
- Mix of urban/tier-2 city backgrounds

Return your analysis as a JSON array with this EXACT structure:
[
  {{
    "name": "Full Indian name (realistic)",
    "age": 28,
    "occupation": "Specific job title",
    "location": "City, India",
    "background": "Brief lifestyle context (1-2 sentences)",
    "image_description": "Physical description for image generation",
    "goals": ["Goal 1", "Goal 2", "Goal 3"],
    "pain_points": ["Pain point 1 from research", "Pain point 2", "Pain point 3"],
    "behaviors": ["Behavior 1", "Behavior 2", "Behavior 3"],
    "quote": "A characteristic quote from this persona",
    "tech_savviness": "Low|Medium|High",
    "shopping_frequency": "Specific frequency (e.g., '2-3x per week')",
    "avg_spend": "Spending range with ₹ symbol",
    "motivations": ["Motivation 1", "Motivation 2"],
    "frustrations": ["Frustration 1", "Frustration 2"]
  }}
]

Guidelines:
- Names should be authentic Indian names (diverse - Hindu, Muslim, Sikh, Christian backgrounds)
- Ages between 22-55 for realistic target audience
- Occupations should be specific (not just "professional")
- Locations should include tier-1 and tier-2 Indian cities
- Quotes should sound natural and reflect Indian English/Hinglish usage patterns
- Pain points should directly reference the research data above
- Behaviors should be observable actions
- Make each persona feel unique and memorable

Return ONLY the JSON array, no additional text.

JSON Output:"""

    def _parse_response(self, response_text: str) -> List[Persona]:
        """
        Parse Claude's response into Persona objects.
        """
        try:
            # Extract JSON from response
            response_text = response_text.strip()

            # Try to find JSON array in the response
            start_idx = response_text.find('[')
            end_idx = response_text.rfind(']') + 1

            if start_idx == -1 or end_idx == 0:
                return []

            json_str = response_text[start_idx:end_idx]
            personas_data = json.loads(json_str)

            # Convert to Persona objects
            personas = []
            for data in personas_data:
                try:
                    # Validate and convert tech_savviness
                    tech_sav = data.get('tech_savviness', 'Medium')
                    if tech_sav not in ['Low', 'Medium', 'High']:
                        tech_sav = 'Medium'

                    persona = Persona(
                        name=data.get('name', 'Unknown User'),
                        age=data.get('age', 30),
                        occupation=data.get('occupation', 'Professional'),
                        location=data.get('location', 'India'),
                        background=data.get('background', ''),
                        image_description=data.get('image_description', ''),
                        goals=data.get('goals', []),
                        pain_points=data.get('pain_points', []),
                        behaviors=data.get('behaviors', []),
                        quote=data.get('quote', ''),
                        tech_savviness=TechSavviness(tech_sav),
                        shopping_frequency=data.get('shopping_frequency'),
                        avg_spend=data.get('avg_spend'),
                        motivations=data.get('motivations', []),
                        frustrations=data.get('frustrations', [])
                    )
                    personas.append(persona)
                except Exception as e:
                    print(f"Error parsing persona: {str(e)}")
                    continue

            return personas

        except json.JSONDecodeError as e:
            print(f"JSON decode error: {str(e)}")
            return []
        except Exception as e:
            print(f"Error parsing personas: {str(e)}")
            return []
