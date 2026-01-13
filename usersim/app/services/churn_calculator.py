from typing import List, Dict, Tuple
from app.models.user_profile import VirtualUser, PatienceLevel
from app.models.scenario import ChurnAnalysis


class ChurnCalculator:
    """Calculates churn probability based on frustration events and user patience"""

    # Frustration event weights (how much churn risk each event adds)
    FRUSTRATION_WEIGHTS = {
        # Generic events (applicable to most products)
        "long_wait": 30,  # Waiting longer than expected
        "feature_unavailable": 25,  # Feature user needs is not available
        "error_encountered": 20,  # System error/crash
        "retry_required": 10,  # Had to retry an action
        "unexpected_cost": 15,  # Price/cost higher than expected
        "poor_quality": 20,  # Quality below expectations
        "lack_of_feedback": 10,  # No system response/feedback

        # Specific to different domains (will be dynamically added)
        "driver_cancellation": 25,
        "no_availability": 30,
        "redirect_failure": 20,
        "slow_response": 15,
        "payment_failure": 35,
        "data_loss": 40,
        "security_concern": 50,
    }

    # Patience multipliers
    PATIENCE_MULTIPLIERS = {
        PatienceLevel.LOW: 2.0,
        PatienceLevel.MEDIUM: 1.5,
        PatienceLevel.HIGH: 1.0,
    }

    # Risk level thresholds
    RISK_LEVELS = [
        (0, 30, "LOW"),
        (31, 50, "MEDIUM"),
        (51, 75, "HIGH"),
        (76, 100, "CRITICAL"),
    ]

    def __init__(self, virtual_user: VirtualUser):
        self.user = virtual_user
        self.patience_multiplier = self.PATIENCE_MULTIPLIERS.get(
            virtual_user.patience_level, 1.5
        )

    def calculate_churn(
        self,
        frustration_events: List[Dict[str, any]],
        context: Dict[str, any],
        ai_context_adjustment: float = 0,
    ) -> ChurnAnalysis:
        """
        Calculate churn probability with two-layer system:
        Layer 1: Formula-based calculation
        Layer 2: AI context adjustment

        Args:
            frustration_events: List of {"event": "event_name", "severity": 1.0}
            context: Additional context for AI (urgency, alternatives, etc.)
            ai_context_adjustment: Adjustment from AI (-50 to +50)

        Returns:
            ChurnAnalysis with detailed breakdown
        """

        # Layer 1: Formula-based calculation
        base_risk = self.user.base_churn_risk

        # Calculate frustration risk
        frustration_risk = 0
        event_details = []

        for event in frustration_events:
            event_name = event.get("event", "")
            severity = event.get("severity", 1.0)  # Multiplier (0.5 to 2.0)

            base_weight = self.FRUSTRATION_WEIGHTS.get(event_name, 15)  # Default 15%
            risk_added = base_weight * severity

            frustration_risk += risk_added
            event_details.append({"event": event_name, "risk_added": risk_added})

        # Apply user-specific frustration triggers
        for trigger in self.user.frustration_triggers:
            # Check if this trigger was hit
            if any(e["event"] == trigger.trigger for e in frustration_events):
                frustration_risk += trigger.impact
                event_details.append(
                    {"event": f"{trigger.trigger}_user_specific", "risk_added": trigger.impact}
                )

        # Formula risk before patience multiplier
        formula_risk = base_risk + frustration_risk

        # Apply patience multiplier
        calculated_risk = formula_risk * self.patience_multiplier

        # Layer 2: AI context adjustment
        ai_adjustments = self._parse_ai_adjustments(context, ai_context_adjustment)

        # Final churn probability (capped at 100%)
        final_churn = min(calculated_risk + ai_context_adjustment, 100.0)

        # Determine risk level
        risk_level = self._get_risk_level(final_churn)

        # Generate reasoning
        reasoning = self._generate_reasoning(
            final_churn, event_details, ai_adjustments, context
        )

        return ChurnAnalysis(
            base_risk=base_risk,
            frustration_events=event_details,
            formula_risk=formula_risk,
            patience_multiplier=self.patience_multiplier,
            calculated_risk=calculated_risk,
            ai_adjustments=ai_adjustments,
            final_churn_probability=final_churn,
            risk_level=risk_level,
            reasoning=reasoning,
        )

    def _parse_ai_adjustments(
        self, context: Dict[str, any], total_adjustment: float
    ) -> List[Dict[str, float]]:
        """Parse AI context into adjustment factors"""
        adjustments = []

        # Sunk cost effect (time already invested)
        time_invested = context.get("time_invested_seconds", 0)
        if time_invested > 0:
            sunk_cost_adj = min(-10, -(time_invested / 60) * 3)  # -3% per minute
            adjustments.append({"factor": "sunk_cost_effect", "adjustment": sunk_cost_adj})

        # Urgency
        urgency = context.get("urgency", "medium")
        if urgency == "high":
            adjustments.append({"factor": "high_urgency", "adjustment": -5})
        elif urgency == "low":
            adjustments.append({"factor": "low_urgency", "adjustment": +10})

        # Alternatives available
        has_alternatives = context.get("alternatives_available", False)
        if has_alternatives:
            adjustments.append({"factor": "easy_alternatives", "adjustment": +10})

        # First vs repeated failure
        failure_count = context.get("failure_count", 1)
        if failure_count == 1:
            adjustments.append({"factor": "first_failure", "adjustment": -5})
        elif failure_count >= 3:
            adjustments.append({"factor": "repeated_failures", "adjustment": +15})

        # Add any remaining adjustment as "other context"
        accounted_adjustment = sum(a["adjustment"] for a in adjustments)
        if abs(total_adjustment - accounted_adjustment) > 0.1:
            adjustments.append(
                {
                    "factor": "other_context",
                    "adjustment": total_adjustment - accounted_adjustment,
                }
            )

        return adjustments

    def _get_risk_level(self, churn_probability: float) -> str:
        """Determine risk level from churn probability"""
        for min_val, max_val, level in self.RISK_LEVELS:
            if min_val <= churn_probability <= max_val:
                return level
        return "CRITICAL"

    def _generate_reasoning(
        self,
        final_churn: float,
        events: List[Dict],
        adjustments: List[Dict],
        context: Dict,
    ) -> str:
        """Generate human-readable reasoning for the churn probability"""

        # Identify main frustration source
        if events:
            main_event = max(events, key=lambda e: e["risk_added"])
            main_frustration = main_event["event"]
        else:
            main_frustration = "general friction"

        # Identify main context factor
        if adjustments:
            significant_adj = [a for a in adjustments if abs(a["adjustment"]) >= 5]
            if significant_adj:
                main_factor = significant_adj[0]["factor"]
            else:
                main_factor = "user patience"
        else:
            main_factor = "user patience"

        # Build reasoning
        if final_churn < 30:
            return f"Low churn risk. User is experiencing {main_frustration} but {main_factor} keeps them engaged."
        elif final_churn < 50:
            return f"Medium churn risk. {main_frustration.replace('_', ' ').title()} is causing frustration. User will likely try one more alternative before giving up completely."
        elif final_churn < 75:
            return f"High churn risk. Significant frustration from {main_frustration}. User is close to abandoning the product entirely. {main_factor.replace('_', ' ').title()} is the deciding factor."
        else:
            return f"Critical churn risk. Multiple failures including {main_frustration} have exhausted user patience. Immediate intervention needed to prevent churn."

    def add_custom_frustration_weight(self, event_name: str, weight: float):
        """Add domain-specific frustration event weight"""
        self.FRUSTRATION_WEIGHTS[event_name] = weight
