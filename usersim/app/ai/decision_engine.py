import anthropic
import os
import json
from typing import List, Dict, Tuple
from app.models.user_profile import VirtualUser
from app.models.scenario import DecisionOption, EmotionalState


class AIDecisionEngine:
    """
    Uses Claude AI to make realistic user decisions based on:
    - User profile (personality, sensitivities, goals)
    - Current context (what just happened)
    - Available options (what can the user do next)
    """

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key is required")
        self.client = anthropic.Anthropic(api_key=self.api_key)

    def make_decision(
        self,
        user: VirtualUser,
        context: Dict[str, any],
        options: List[DecisionOption],
        current_churn_risk: float,
    ) -> Tuple[str, str, float, EmotionalState]:
        """
        Simulate a realistic user decision

        Args:
            user: Virtual user profile
            context: Current situation (what just happened, time elapsed, etc.)
            options: Available choices
            current_churn_risk: Current churn probability

        Returns:
            (chosen_option_id, reasoning, context_adjustment, emotional_state)
        """

        # Build prompt for Claude
        prompt = self._build_decision_prompt(user, context, options, current_churn_risk)

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=1000,
                temperature=0.7,  # Add some randomness for realistic behavior
                messages=[{"role": "user", "content": prompt}],
            )

            # Parse Claude's response
            result = self._parse_decision_response(response.content[0].text, options)
            return result

        except Exception as e:
            print(f"AI Decision Engine error: {e}")
            # Fallback to first option
            return (
                options[0].option_id,
                f"Fallback decision due to error: {str(e)}",
                0,
                EmotionalState.FRUSTRATED,
            )

    def _build_decision_prompt(
        self,
        user: VirtualUser,
        context: Dict[str, any],
        options: List[DecisionOption],
        current_churn_risk: float,
    ) -> str:
        """Build detailed prompt for Claude to make realistic decision"""

        # Format user profile
        sensitivities_text = "\n".join(
            [f"  - {s.name}: {s.level}/10 - {s.description}" for s in user.sensitivities]
        )

        traits_text = "\n".join(
            [f"  - {t.name}: {t.value}/10 - {t.description}" for t in user.traits]
        )

        # Format options
        options_text = "\n".join(
            [
                f"{i+1}. {opt.description}\n   Consequences: {opt.consequences}"
                for i, opt in enumerate(options)
            ]
        )

        # Format context
        context_text = "\n".join([f"  - {k}: {v}" for k, v in context.items()])

        prompt = f"""You are simulating the decision-making of a realistic user. Based on their profile and current situation, decide what they would most likely do.

**USER PROFILE:**
Name: {user.name}
Age: {user.age}
Occupation: {user.occupation}
Location: {user.location}

Problem Context: {user.problem_context}
Primary Goal: {user.primary_goal}

Sensitivities (what they care about):
{sensitivities_text}

Behavioral Traits:
{traits_text}

Patience Level: {user.patience_level.value}

**CURRENT SITUATION:**
{context_text}

Current Frustration/Churn Risk: {current_churn_risk}%

**AVAILABLE OPTIONS:**
{options_text}

**YOUR TASK:**
1. Consider this user's profile, goals, and sensitivities
2. Evaluate the current situation and frustration level
3. Decide which option this user would REALISTICALLY choose
4. Explain the reasoning behind the decision

**RESPOND IN THIS EXACT JSON FORMAT:**
{{
  "chosen_option": 1,
  "reasoning": "Detailed explanation of why this user would make this choice based on their profile",
  "emotional_state": "frustrated|annoyed|neutral|hopeful|satisfied|angry|delighted",
  "context_adjustment": -10,
  "context_explanation": "Why the context adjustment (e.g., 'High urgency reduces churn by -5%, but easy alternatives increase it by +10%, net -10%')"
}}

The context_adjustment should be a number between -50 and +50 representing how contextual factors affect churn probability beyond the base calculation. Consider:
- Sunk cost (time already invested): reduces churn (-5 to -15)
- Urgency (how badly they need this now): high urgency reduces churn (-5), low increases it (+10)
- Alternatives (other options available): increases churn (+5 to +15)
- Failure count (is this first failure or repeated?): first time reduces (-5), repeated increases (+10 to +20)
- Emotional investment: reduces churn (-5 to -10)

Be realistic. Users don't give up immediately, but they also have limits."""

        return prompt

    def _parse_decision_response(
        self, response_text: str, options: List[DecisionOption]
    ) -> Tuple[str, str, float, EmotionalState]:
        """Parse Claude's JSON response"""

        try:
            # Extract JSON from response
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1
            json_text = response_text[json_start:json_end]

            result = json.loads(json_text)

            # Get chosen option
            chosen_idx = result.get("chosen_option", 1) - 1  # Convert 1-indexed to 0-indexed
            chosen_option_id = options[chosen_idx].option_id if 0 <= chosen_idx < len(options) else options[0].option_id

            reasoning = result.get("reasoning", "User chose this option based on their profile")

            # Parse emotional state
            emotional_state_str = result.get("emotional_state", "neutral").lower()
            emotional_state = self._parse_emotional_state(emotional_state_str)

            # Context adjustment
            context_adjustment = float(result.get("context_adjustment", 0))
            context_adjustment = max(-50, min(50, context_adjustment))  # Clamp to [-50, 50]

            # Append context explanation to reasoning if available
            context_explanation = result.get("context_explanation", "")
            if context_explanation:
                reasoning += f"\n\nContext Analysis: {context_explanation}"

            return (chosen_option_id, reasoning, context_adjustment, emotional_state)

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Error parsing AI response: {e}")
            print(f"Response was: {response_text}")
            # Fallback
            return (
                options[0].option_id,
                response_text[:200],  # Use raw response as reasoning
                0,
                EmotionalState.NEUTRAL,
            )

    def _parse_emotional_state(self, state_str: str) -> EmotionalState:
        """Convert string to EmotionalState enum"""
        state_map = {
            "neutral": EmotionalState.NEUTRAL,
            "satisfied": EmotionalState.SATISFIED,
            "hopeful": EmotionalState.HOPEFUL,
            "frustrated": EmotionalState.FRUSTRATED,
            "annoyed": EmotionalState.ANNOYED,
            "angry": EmotionalState.ANGRY,
            "delighted": EmotionalState.DELIGHTED,
        }
        return state_map.get(state_str.lower(), EmotionalState.NEUTRAL)

    def generate_virtual_user(
        self, problem_statement: str, target_users: str, persona_data: Dict = None
    ) -> VirtualUser:
        """
        Generate a virtual user profile from problem statement
        Optionally import from ResearchAI persona
        """

        if persona_data:
            # Convert ResearchAI persona to VirtualUser
            return self._convert_persona_to_virtual_user(persona_data, problem_statement)

        # Generate new virtual user using Claude
        prompt = f"""Create a realistic virtual user profile for testing this product.

**Problem Statement:** {problem_statement}
**Target Users:** {target_users}

Create a detailed user profile that represents a typical user for this product. Include:
1. Demographics (name, age, occupation, location)
2. Problem context (how this problem affects them)
3. Primary goal (what they want to achieve)
4. Sensitivities (what they care about most - price, time, quality, etc.) - rate each 0-10
5. Behavioral traits (patience, tech savvy, brand loyalty, etc.) - rate each 0-10
6. Frustration triggers (what would make them give up)

**RESPOND IN THIS EXACT JSON FORMAT:**
{{
  "name": "Realistic name",
  "age": 28,
  "occupation": "Job title",
  "location": "City, Country",
  "problem_context": "How this problem affects their daily life",
  "primary_goal": "What they want to achieve",
  "sensitivities": [
    {{"name": "price_sensitivity", "level": 8, "description": "Very price-conscious"}},
    {{"name": "time_sensitivity", "level": 6, "description": "Values time but willing to wait for value"}}
  ],
  "traits": [
    {{"name": "tech_savvy", "value": 7, "description": "Comfortable with apps and technology"}},
    {{"name": "patience", "value": 5, "description": "Average patience level"}}
  ],
  "patience_level": "medium",
  "frustration_triggers": [
    {{"trigger": "long_wait", "threshold": 5, "impact": 30}},
    {{"trigger": "unexpected_cost", "threshold": 50, "impact": 25}}
  ]
}}

IMPORTANT: "patience_level" MUST be exactly one of these three values: "low", "medium", or "high" (no other variations allowed).

Make the user realistic and specific to the problem domain."""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=1500,
                messages=[{"role": "user", "content": prompt}],
            )

            # Parse response
            json_start = response.content[0].text.find("{")
            json_end = response.content[0].text.rfind("}") + 1
            json_text = response.content[0].text[json_start:json_end]

            user_data = json.loads(json_text)

            # Convert to VirtualUser
            from app.models.user_profile import (
                SensitivityAttribute,
                BehavioralTrait,
                FrustrationTrigger,
                PatienceLevel,
            )

            return VirtualUser(
                name=user_data["name"],
                age=user_data["age"],
                occupation=user_data["occupation"],
                location=user_data["location"],
                problem_context=user_data["problem_context"],
                primary_goal=user_data["primary_goal"],
                sensitivities=[SensitivityAttribute(**s) for s in user_data["sensitivities"]],
                traits=[BehavioralTrait(**t) for t in user_data["traits"]],
                patience_level=PatienceLevel(user_data["patience_level"]),
                frustration_triggers=[
                    FrustrationTrigger(**t) for t in user_data["frustration_triggers"]
                ],
            )

        except Exception as e:
            print(f"Error generating virtual user: {e}")
            raise

    def _convert_persona_to_virtual_user(
        self, persona_data: Dict, problem_statement: str
    ) -> VirtualUser:
        """Convert ResearchAI persona to VirtualUser format"""
        # This would map persona fields to virtual user fields
        # Implementation depends on ResearchAI persona structure
        pass
