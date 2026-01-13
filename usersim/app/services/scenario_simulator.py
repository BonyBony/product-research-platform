import anthropic
import os
import json
from typing import List, Dict, Tuple
from app.models.user_profile import VirtualUser
from app.models.scenario import (
    Scenario,
    JourneyStep,
    StepType,
    EmotionalState,
    DecisionOption,
    ScenarioType,
    ScenarioSimulationResponse,
)
from app.services.churn_calculator import ChurnCalculator
from app.ai.decision_engine import AIDecisionEngine


class ScenarioSimulator:
    """
    Generates and simulates user journey scenarios using AI
    """

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.decision_engine = AIDecisionEngine(api_key)

    def generate_and_simulate_scenarios(
        self,
        problem_statement: str,
        product_flow: str,
        virtual_user: VirtualUser,
        num_scenarios: int = 5,
    ) -> ScenarioSimulationResponse:
        """
        Main entry point: Generate scenarios and simulate user behavior

        Args:
            problem_statement: What problem does this product solve
            product_flow: High-level description of how product works
            virtual_user: The virtual user to simulate
            num_scenarios: How many scenarios to generate

        Returns:
            Complete simulation with all scenarios and insights
        """

        # Step 1: Generate scenario templates using Claude
        scenario_templates = self._generate_scenario_templates(
            problem_statement, product_flow, virtual_user, num_scenarios
        )

        # Step 2: Simulate each scenario
        simulated_scenarios = []
        for template in scenario_templates:
            scenario = self._simulate_scenario(template, virtual_user, product_flow)
            simulated_scenarios.append(scenario)

        # Step 3: Analyze across scenarios
        summary_insights = self._generate_summary_insights(simulated_scenarios)
        churn_hotspots = self._identify_churn_hotspots(simulated_scenarios)
        recommendations = self._generate_recommendations(simulated_scenarios, virtual_user)

        return ScenarioSimulationResponse(
            virtual_user=virtual_user.dict(),
            scenarios=simulated_scenarios,
            summary_insights=summary_insights,
            churn_hotspots=churn_hotspots,
            recommendations=recommendations,
        )

    def _generate_scenario_templates(
        self,
        problem_statement: str,
        product_flow: str,
        virtual_user: VirtualUser,
        num_scenarios: int,
    ) -> List[Dict]:
        """Use Claude to generate realistic scenario templates"""

        prompt = f"""You are designing test scenarios for a product. Create {num_scenarios} realistic user journey scenarios.

**Product Details:**
Problem: {problem_statement}
Product Flow: {product_flow}

**Target User:**
{virtual_user.name} - {virtual_user.problem_context}
Goal: {virtual_user.primary_goal}

**Scenario Requirements:**
1. First scenario should be the HAPPY PATH (everything works perfectly)
2. Remaining scenarios should be EDGE CASES and FAILURES:
   - Things that can go wrong
   - System failures
   - User mistakes
   - External factors (network issues, availability problems, etc.)

Keep scenarios simple: 3-5 key steps per scenario.

**RESPOND IN THIS EXACT JSON FORMAT:**
{{
  "scenarios": [
    {{
      "scenario_name": "Happy Path - Successful Journey",
      "scenario_type": "happy_path",
      "description": "User achieves their goal without issues",
      "steps": [
        {{
          "step_type": "action",
          "description": "User opens the app",
          "expected_outcome": "App loads successfully"
        }},
        {{
          "step_type": "action",
          "description": "User enters destination",
          "expected_outcome": "System shows available options"
        }},
        {{
          "step_type": "decision_point",
          "description": "System shows no available options",
          "decision_needed": "What should user do?",
          "options": [
            "Retry immediately",
            "Try alternative service",
            "Give up"
          ]
        }}
      ]
    }}
  ]
}}

Make scenarios realistic and specific to this product."""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}],
            )

            # Parse response
            json_start = response.content[0].text.find("{")
            json_end = response.content[0].text.rfind("}") + 1
            json_text = response.content[0].text[json_start:json_end]

            result = json.loads(json_text)
            return result.get("scenarios", [])

        except Exception as e:
            print(f"Error generating scenarios: {e}")
            # Return minimal fallback scenario
            return [
                {
                    "scenario_name": "Basic Happy Path",
                    "scenario_type": "happy_path",
                    "description": "User completes basic flow",
                    "steps": [
                        {
                            "step_type": "action",
                            "description": "User starts using product",
                            "expected_outcome": "Product responds",
                        }
                    ],
                }
            ]

    def _simulate_scenario(
        self, template: Dict, virtual_user: VirtualUser, product_flow: str
    ) -> Scenario:
        """Simulate a single scenario with the virtual user"""

        churn_calc = ChurnCalculator(virtual_user)

        scenario_id = template["scenario_name"].lower().replace(" ", "_")
        scenario_type = ScenarioType(template.get("scenario_type", "happy_path"))

        simulated_steps = []
        cumulative_time = 0
        frustration_events = []
        current_churn = virtual_user.base_churn_risk

        for idx, step_template in enumerate(template["steps"]):
            step_num = idx + 1
            step_type = StepType(step_template.get("step_type", "action"))

            # Simulate step duration (2-30 seconds typically)
            step_duration = self._estimate_step_duration(step_type, step_template)
            cumulative_time += step_duration

            # Check if this is a decision point
            is_decision = step_type == StepType.DECISION_POINT or "decision_needed" in step_template

            if is_decision:
                # AI makes decision
                step = self._simulate_decision_step(
                    step_num,
                    step_template,
                    virtual_user,
                    churn_calc,
                    frustration_events,
                    cumulative_time,
                    step_duration,
                )
                simulated_steps.append(step)

                # Update frustration events based on decision
                if step.churn_analysis and step.churn_analysis.final_churn_probability > current_churn:
                    current_churn = step.churn_analysis.final_churn_probability

            else:
                # Regular step (action or system response)
                step = self._simulate_regular_step(
                    step_num,
                    step_type,
                    step_template,
                    virtual_user,
                    churn_calc,
                    frustration_events,
                    cumulative_time,
                    step_duration,
                )
                simulated_steps.append(step)

                # Check if this step adds frustration
                if step_type == StepType.ERROR or "error" in step_template.get("description", "").lower():
                    frustration_events.append({"event": "error_encountered", "severity": 1.0})

        # Determine outcome
        final_churn = simulated_steps[-1].churn_analysis.final_churn_probability if simulated_steps[-1].churn_analysis else current_churn

        if final_churn > 75:
            outcome = "User churned - Gave up completely"
        elif final_churn > 50:
            outcome = "Partial success - User frustrated but completed"
        else:
            outcome = "Success - User achieved goal"

        # Generate insights
        key_insights = self._generate_scenario_insights(simulated_steps, virtual_user)

        return Scenario(
            scenario_id=scenario_id,
            scenario_name=template["scenario_name"],
            scenario_type=scenario_type,
            description=template["description"],
            steps=simulated_steps,
            outcome=outcome,
            final_churn_probability=final_churn,
            key_insights=key_insights,
        )

    def _simulate_decision_step(
        self,
        step_num: int,
        step_template: Dict,
        virtual_user: VirtualUser,
        churn_calc: ChurnCalculator,
        frustration_events: List[Dict],
        cumulative_time: float,
        step_duration: float,
    ) -> JourneyStep:
        """Simulate a decision point where user must choose"""

        # Build decision options
        options = []
        for idx, opt_desc in enumerate(step_template.get("options", [])):
            options.append(
                DecisionOption(
                    option_id=f"option_{idx+1}",
                    description=opt_desc,
                    consequences=f"Potential outcome of choosing: {opt_desc}",
                )
            )

        # Build context for AI decision
        context = {
            "current_step": step_template["description"],
            "time_invested_seconds": cumulative_time,
            "urgency": "high" if "urgent" in virtual_user.problem_context.lower() else "medium",
            "alternatives_available": len(options) > 2,
            "failure_count": len([e for e in frustration_events if "error" in e.get("event", "")]),
        }

        # Calculate current churn
        churn_analysis = churn_calc.calculate_churn(frustration_events, context, 0)
        current_churn = churn_analysis.final_churn_probability

        # AI makes decision
        chosen_id, reasoning, context_adj, emotional_state = self.decision_engine.make_decision(
            virtual_user, context, options, current_churn
        )

        # Recalculate churn with AI adjustment
        final_churn_analysis = churn_calc.calculate_churn(
            frustration_events, context, context_adj
        )

        return JourneyStep(
            step_number=step_num,
            step_type=StepType.DECISION_POINT,
            description=step_template["description"],
            emotional_state=emotional_state,
            frustration_level=min(final_churn_analysis.final_churn_probability / 10, 10),
            churn_analysis=final_churn_analysis,
            is_decision_point=True,
            decision_options=options,
            chosen_option=chosen_id,
            decision_reasoning=reasoning,
            time_elapsed=cumulative_time,
            step_duration=step_duration,
        )

    def _simulate_regular_step(
        self,
        step_num: int,
        step_type: StepType,
        step_template: Dict,
        virtual_user: VirtualUser,
        churn_calc: ChurnCalculator,
        frustration_events: List[Dict],
        cumulative_time: float,
        step_duration: float,
    ) -> JourneyStep:
        """Simulate a regular action or system response step"""

        description = step_template.get("description", "User takes action")

        # Determine emotional state based on outcome
        expected_outcome = step_template.get("expected_outcome", "success")
        if "error" in description.lower() or "fail" in expected_outcome.lower():
            emotional_state = EmotionalState.FRUSTRATED
            frustration = 7.0
        elif "success" in expected_outcome.lower():
            emotional_state = EmotionalState.HOPEFUL
            frustration = 3.0
        else:
            emotional_state = EmotionalState.NEUTRAL
            frustration = 5.0

        # Calculate churn
        context = {"time_invested_seconds": cumulative_time}
        churn_analysis = churn_calc.calculate_churn(frustration_events, context, 0)

        return JourneyStep(
            step_number=step_num,
            step_type=step_type,
            description=description,
            user_action=description if step_type == StepType.ACTION else None,
            system_response=expected_outcome if step_type == StepType.SYSTEM_RESPONSE else None,
            emotional_state=emotional_state,
            frustration_level=frustration,
            churn_analysis=churn_analysis,
            is_decision_point=False,
            time_elapsed=cumulative_time,
            step_duration=step_duration,
        )

    def _estimate_step_duration(self, step_type: StepType, step_template: Dict) -> float:
        """Estimate realistic duration for each step in seconds"""
        if step_type == StepType.ACTION:
            return 5.0  # User action takes ~5 seconds
        elif step_type == StepType.SYSTEM_RESPONSE:
            return 2.0  # System responds in ~2 seconds
        elif step_type == StepType.DECISION_POINT:
            return 10.0  # User thinks for ~10 seconds
        elif "wait" in step_template.get("description", "").lower():
            return 120.0  # Waiting ~2 minutes
        else:
            return 3.0

    def _generate_scenario_insights(
        self, steps: List[JourneyStep], virtual_user: VirtualUser
    ) -> List[str]:
        """Generate insights from a completed scenario"""
        insights = []

        # Find highest churn step
        churn_steps = [s for s in steps if s.churn_analysis]
        if churn_steps:
            max_churn_step = max(churn_steps, key=lambda s: s.churn_analysis.final_churn_probability)
            insights.append(
                f"Highest churn risk at step {max_churn_step.step_number}: {max_churn_step.description} ({max_churn_step.churn_analysis.final_churn_probability:.0f}%)"
            )

        # Count decision points
        decisions = [s for s in steps if s.is_decision_point]
        if decisions:
            insights.append(f"User faced {len(decisions)} decision point(s)")

        # Total time
        total_time = steps[-1].time_elapsed if steps else 0
        insights.append(f"Total journey time: {total_time:.0f} seconds ({total_time/60:.1f} minutes)")

        return insights

    def _generate_summary_insights(self, scenarios: List[Scenario]) -> List[str]:
        """Generate insights across all scenarios"""
        insights = []

        # Average churn across scenarios
        avg_churn = sum(s.final_churn_probability for s in scenarios) / len(scenarios) if scenarios else 0
        insights.append(f"Average churn probability across scenarios: {avg_churn:.1f}%")

        # Count by outcome
        success = len([s for s in scenarios if "success" in s.outcome.lower()])
        churn = len([s for s in scenarios if "churn" in s.outcome.lower()])
        insights.append(f"Outcomes: {success} successful, {churn} churned out of {len(scenarios)} scenarios")

        return insights

    def _identify_churn_hotspots(self, scenarios: List[Scenario]) -> List[str]:
        """Identify common steps where churn risk spikes"""
        hotspots = []

        # Collect all high-churn steps
        high_churn_steps = []
        for scenario in scenarios:
            for step in scenario.steps:
                if step.churn_analysis and step.churn_analysis.final_churn_probability > 50:
                    high_churn_steps.append(step.description)

        # Find most common
        from collections import Counter

        if high_churn_steps:
            common = Counter(high_churn_steps).most_common(3)
            for desc, count in common:
                hotspots.append(f"{desc} (occurred in {count} scenario(s))")

        return hotspots

    def _generate_recommendations(
        self, scenarios: List[Scenario], virtual_user: VirtualUser
    ) -> List[str]:
        """Generate product improvement recommendations"""
        recommendations = []

        # Analyze frustration events
        all_events = []
        for scenario in scenarios:
            for step in scenario.steps:
                if step.churn_analysis:
                    all_events.extend(step.churn_analysis.frustration_events)

        if all_events:
            from collections import Counter

            common_events = Counter(e["event"] for e in all_events).most_common(3)
            for event, count in common_events:
                event_name = event.replace("_", " ").title()
                recommendations.append(
                    f"Reduce {event_name} - occurred {count} times across scenarios"
                )

        return recommendations
