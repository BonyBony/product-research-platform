"""
Prioritization Service
Combines JTBD + RICE frameworks for evidence-based pain point prioritization
"""

from anthropic import Anthropic
from typing import List, Dict
import json
from app.config import get_settings
from app.models.prioritization import (
    PrioritizedPainPoint, JTBDScore, RICEScore, PersonaAlignment,
    Justification, MarketData, OpportunityCategory, ImpactLevel
)
from app.services.market_sizing import MarketSizingEngine


class PrioritizationService:
    """
    Prioritizes pain points using JTBD + RICE hybrid framework.

    Methodology:
    - 40% JTBD Opportunity Score (customer-centric)
    - 40% RICE Score (data-driven)
    - 20% Persona Alignment (strategic)
    """

    def __init__(self):
        settings = get_settings()
        self.client = Anthropic(api_key=settings.anthropic_api_key)
        self.model = "claude-sonnet-4-5"
        self.market_engine = MarketSizingEngine()

    def prioritize_pain_points(
        self,
        pain_points: List[Dict],
        personas: List[Dict],
        problem_statement: str,
        target_users: str,
        market_context: Dict = None
    ) -> List[PrioritizedPainPoint]:
        """
        Main prioritization method.

        Returns prioritized list of pain points with full analysis.
        """
        if not pain_points:
            return []

        prioritized = []

        for idx, pain_point in enumerate(pain_points):
            # Step 1: JTBD Analysis
            jtbd_score = self._calculate_jtbd_score(
                pain_point=pain_point,
                problem_statement=problem_statement,
                target_users=target_users
            )

            # Step 2: RICE Analysis
            rice_score = self._calculate_rice_score(
                pain_point=pain_point,
                problem_statement=problem_statement,
                target_users=target_users,
                jtbd_score=jtbd_score
            )

            # Step 3: Persona Alignment
            persona_alignment = self._calculate_persona_alignment(
                pain_point=pain_point,
                personas=personas
            )

            # Step 4: Calculate Final Score
            final_score = self._calculate_final_score(
                jtbd_score=jtbd_score,
                rice_score=rice_score,
                persona_alignment=persona_alignment
            )

            # Step 5: Build Justification
            justification = self._build_justification(
                pain_point=pain_point,
                jtbd_score=jtbd_score,
                rice_score=rice_score,
                persona_alignment=persona_alignment,
                problem_statement=problem_statement,
                target_users=target_users
            )

            # Create prioritized pain point
            prioritized_pp = PrioritizedPainPoint(
                pain_point_id=f"pp_{idx}",
                description=pain_point.get('description', ''),
                original_severity=pain_point.get('severity', 'Medium'),
                priority_rank=0,  # Will be set after sorting
                final_score=final_score,
                jtbd=jtbd_score,
                rice=rice_score,
                persona_alignment=persona_alignment,
                justification=justification
            )

            prioritized.append(prioritized_pp)

        # Sort by final score (descending)
        prioritized.sort(key=lambda x: x.final_score, reverse=True)

        # Assign priority ranks
        for rank, pp in enumerate(prioritized, 1):
            pp.priority_rank = rank

        return prioritized

    def _calculate_jtbd_score(
        self,
        pain_point: Dict,
        problem_statement: str,
        target_users: str
    ) -> JTBDScore:
        """
        Calculate JTBD Opportunity Score using Claude AI.
        """
        prompt = f"""You are a product strategist using the Jobs-to-be-Done framework.

Problem Statement: {problem_statement}
Target Users: {target_users}
Pain Point: {pain_point.get('description', '')}
User Quote: "{pain_point.get('quote', '')}"
Severity: {pain_point.get('severity', 'Medium')}

Your task:
1. Write a JTBD statement: "When [situation], [user] wants to [motivation], so they can [outcome]"
2. Rate IMPORTANCE (0-10): How critical is this job to the user?
3. Rate SATISFACTION (0-10): How well are current solutions satisfying this need?
4. Calculate OPPORTUNITY SCORE = Importance + max(Importance - Satisfaction, 0)
5. Categorize: underserved (score > 10), wellserved (8-10), or overserved (< 8)
6. Explain your reasoning

Return as JSON:
{{
  "job_statement": "When users...",
  "importance": 8.5,
  "satisfaction": 2.0,
  "opportunity_score": 15.0,
  "category": "underserved",
  "reasoning": "This job is critical because..."
}}"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = response.content[0].text if hasattr(response.content[0], 'text') else str(response.content[0])

        # Parse JSON
        try:
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            json_str = response_text[start_idx:end_idx]
            data = json.loads(json_str)

            return JTBDScore(
                job_statement=data.get('job_statement', ''),
                importance=float(data.get('importance', 5.0)),
                satisfaction=float(data.get('satisfaction', 5.0)),
                opportunity_score=float(data.get('opportunity_score', 10.0)),
                category=OpportunityCategory(data.get('category', 'wellserved')),
                reasoning=data.get('reasoning', '')
            )
        except Exception as e:
            print(f"Error parsing JTBD response: {e}")
            # Return default
            return JTBDScore(
                job_statement=f"When users face {pain_point.get('description', '')}, they want a solution",
                importance=7.0,
                satisfaction=3.0,
                opportunity_score=11.0,
                category=OpportunityCategory.UNDERSERVED,
                reasoning="Default scoring due to parsing error"
            )

    def _calculate_rice_score(
        self,
        pain_point: Dict,
        problem_statement: str,
        target_users: str,
        jtbd_score: JTBDScore
    ) -> RICEScore:
        """
        Calculate RICE Score with AI-assisted estimation.
        """
        # 1. REACH - Use market sizing engine
        frequency = pain_point.get('frequency', 1)
        severity = pain_point.get('severity', 'Medium')

        # Count total comments (rough proxy for data volume)
        num_comments = 50  # Default, ideally passed from research

        reach, reach_justification = self.market_engine.estimate_reach(
            problem_statement=problem_statement,
            target_users=target_users,
            frequency=frequency,
            num_comments=num_comments,
            severity=severity
        )

        # 2. IMPACT - Based on severity and JTBD importance
        impact = self._estimate_impact(
            severity=severity,
            importance=jtbd_score.importance,
            quote=pain_point.get('quote', '')
        )

        impact_reasoning = self._build_impact_reasoning(
            severity=severity,
            importance=jtbd_score.importance,
            impact=impact,
            quote=pain_point.get('quote', '')
        )

        # 3. CONFIDENCE - Based on data quality
        confidence = self._estimate_confidence(
            frequency=frequency,
            num_sources=2,  # YouTube + HackerNews
            severity=severity
        )

        confidence_basis = self._build_confidence_basis(
            frequency=frequency,
            confidence=confidence
        )

        # 4. EFFORT - AI estimation
        effort, effort_breakdown = self._estimate_effort(
            pain_point=pain_point,
            problem_statement=problem_statement
        )

        # Calculate RICE score
        rice_score = (reach * impact * confidence) / effort if effort > 0 else 0

        return RICEScore(
            reach=reach,
            reach_justification=reach_justification,
            impact=impact,
            impact_reasoning=impact_reasoning,
            confidence=confidence,
            confidence_basis=confidence_basis,
            effort=effort,
            effort_breakdown=effort_breakdown,
            rice_score=rice_score
        )

    def _estimate_impact(self, severity: str, importance: float, quote: str) -> float:
        """
        Estimate impact multiplier (0.25 - 3.0).
        """
        # Base impact from severity
        severity_map = {
            "High": 2.0,
            "Medium": 1.0,
            "Low": 0.5
        }
        base_impact = severity_map.get(severity, 1.0)

        # Adjust based on JTBD importance
        if importance >= 9.0:
            importance_multiplier = 1.5
        elif importance >= 7.0:
            importance_multiplier = 1.2
        else:
            importance_multiplier = 1.0

        # Check quote intensity
        blocking_words = ["can't", "unable", "impossible", "blocks", "prevents", "stuck"]
        if any(word in quote.lower() for word in blocking_words):
            quote_multiplier = 1.2
        else:
            quote_multiplier = 1.0

        impact = base_impact * importance_multiplier * quote_multiplier

        # Cap within valid range
        return min(max(impact, 0.25), 3.0)

    def _build_impact_reasoning(
        self,
        severity: str,
        importance: float,
        impact: float,
        quote: str
    ) -> str:
        """
        Build explanation for impact score.
        """
        return f"""**Impact: {impact:.1f}**

- Severity: {severity}
- JTBD Importance: {importance}/10
- User Quote: "{quote[:100]}..."

This pain point has {'HIGH' if impact >= 2.0 else 'MEDIUM' if impact >= 1.0 else 'LOW'} impact on user experience."""

    def _estimate_confidence(
        self,
        frequency: int,
        num_sources: int,
        severity: str
    ) -> float:
        """
        Estimate confidence (0.0 - 1.0).
        """
        # Base confidence from frequency
        if frequency >= 10:
            freq_conf = 0.95
        elif frequency >= 5:
            freq_conf = 0.85
        elif frequency >= 3:
            freq_conf = 0.75
        else:
            freq_conf = 0.60

        # Adjust for source diversity
        source_multiplier = min(num_sources / 3.0, 1.0)

        # High severity adds confidence (users complain more)
        severity_boost = 0.05 if severity == "High" else 0.0

        confidence = (freq_conf * source_multiplier) + severity_boost

        return min(confidence, 1.0)

    def _build_confidence_basis(self, frequency: int, confidence: float) -> str:
        """
        Explain confidence score.
        """
        return f"""**Confidence: {confidence*100:.0f}%**

- Mentioned {frequency}x in research
- Data from multiple sources (YouTube, HackerNews)
- Consistent pattern across discussions"""

    def _estimate_effort(
        self,
        pain_point: Dict,
        problem_statement: str
    ) -> tuple[float, Dict[str, float]]:
        """
        Estimate effort in person-months using AI.
        """
        prompt = f"""You are a technical product manager estimating implementation effort.

Problem: {problem_statement}
Pain Point to Solve: {pain_point.get('description', '')}

Estimate effort in person-months for these components:
1. UI/Frontend work
2. Backend/API development
3. Infrastructure/DevOps
4. Testing & QA

Consider:
- Simple UI changes = 0.1-0.5 months
- API integrations = 0.5-2 months
- New services = 2-4 months
- ML/AI features = 4-6 months

Return as JSON:
{{
  "ui_frontend": 0.5,
  "backend_api": 1.5,
  "infrastructure": 0.5,
  "testing_qa": 0.5,
  "total_effort": 3.0,
  "rationale": "Brief explanation"
}}"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )

            response_text = response.content[0].text if hasattr(response.content[0], 'text') else str(response.content[0])

            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            json_str = response_text[start_idx:end_idx]
            data = json.loads(json_str)

            breakdown = {
                "UI/Frontend": data.get('ui_frontend', 0.5),
                "Backend/API": data.get('backend_api', 1.0),
                "Infrastructure": data.get('infrastructure', 0.3),
                "Testing & QA": data.get('testing_qa', 0.3)
            }

            total = data.get('total_effort', sum(breakdown.values()))

            return total, breakdown

        except Exception as e:
            print(f"Error estimating effort: {e}")
            # Return conservative default
            return 2.0, {
                "UI/Frontend": 0.5,
                "Backend/API": 1.0,
                "Infrastructure": 0.3,
                "Testing & QA": 0.2
            }

    def _calculate_persona_alignment(
        self,
        pain_point: Dict,
        personas: List[Dict]
    ) -> PersonaAlignment:
        """
        Calculate how well this pain point aligns with personas.
        """
        if not personas:
            return PersonaAlignment(
                affected_personas=[],
                coverage=0.0,
                affinities={},
                weight=0.0
            )

        affected = []
        affinities = {}

        description_lower = pain_point.get('description', '').lower()

        for persona in personas:
            persona_name = persona.get('name', 'Unknown')

            # Check if pain point matches persona pain points
            persona_pain_points = persona.get('pain_points', [])
            match_count = 0

            for pp in persona_pain_points:
                # Simple keyword matching
                if any(word in description_lower for word in pp.lower().split()[:5]):
                    match_count += 1

            # Determine affinity
            if match_count >= 2:
                affinity = "VERY HIGH"
                affected.append(persona_name)
            elif match_count >= 1:
                affinity = "HIGH"
                affected.append(persona_name)
            else:
                # Check behaviors and goals
                behaviors = ' '.join(persona.get('behaviors', [])).lower()
                goals = ' '.join(persona.get('goals', [])).lower()

                if any(word in behaviors or word in goals for word in description_lower.split()[:5]):
                    affinity = "MEDIUM"
                    affected.append(persona_name)
                else:
                    affinity = "LOW"

            affinities[persona_name] = affinity

        coverage = len(affected) / len(personas) if personas else 0.0

        # Calculate weight (0-10 scale)
        affinity_scores = {"VERY HIGH": 10, "HIGH": 7, "MEDIUM": 4, "LOW": 1}
        total_weight = sum(affinity_scores.get(aff, 0) for aff in affinities.values())
        weight = total_weight / len(personas) if personas else 0.0

        return PersonaAlignment(
            affected_personas=affected,
            coverage=coverage,
            affinities=affinities,
            weight=weight
        )

    def _calculate_final_score(
        self,
        jtbd_score: JTBDScore,
        rice_score: RICEScore,
        persona_alignment: PersonaAlignment
    ) -> float:
        """
        Calculate final priority score.

        Formula: (JTBD × 0.4) + (RICE_normalized × 0.4) + (Persona × 0.2)
        Range: 0-200
        """
        # Normalize JTBD opportunity score (0-20 → 0-100)
        jtbd_normalized = (jtbd_score.opportunity_score / 20.0) * 100

        # Normalize RICE score (0-10M → 0-100)
        # Use logarithmic scale for RICE
        import math
        rice_normalized = min(math.log10(max(rice_score.rice_score, 1)) * 20, 100)

        # Normalize persona weight (0-10 → 0-100)
        persona_normalized = (persona_alignment.weight / 10.0) * 100

        # Weighted combination
        final = (jtbd_normalized * 0.4) + (rice_normalized * 0.4) + (persona_normalized * 0.2)

        return round(final, 2)

    def _build_justification(
        self,
        pain_point: Dict,
        jtbd_score: JTBDScore,
        rice_score: RICEScore,
        persona_alignment: PersonaAlignment,
        problem_statement: str,
        target_users: str
    ) -> Justification:
        """
        Build evidence-based justification.
        """
        # Get market data
        market_data_dict = self.market_engine.get_market_data(problem_statement, target_users)

        market_data = MarketData(
            tam=market_data_dict.get('tam'),
            sam=market_data_dict.get('sam'),
            som=market_data_dict.get('som'),
            market_size_usd=market_data_dict.get('market_size_usd'),
            growth_rate=market_data_dict.get('growth_rate'),
            market_gap="No existing solution addresses this pain point comprehensively",
            sources=market_data_dict.get('sources', [])
        )

        # Build evidence list
        evidence = [
            f"JTBD Opportunity Score: {jtbd_score.opportunity_score}/20 ({jtbd_score.category.value})",
            f"Affects {rice_score.reach:,} users ({target_users})",
            f"Impact: {rice_score.impact}x multiplier",
            f"Confidence: {rice_score.confidence*100:.0f}% based on research data",
            f"Affects {len(persona_alignment.affected_personas)}/{len(persona_alignment.affinities)} personas",
            f"Mentioned {pain_point.get('frequency', 1)}x in user research",
            f"Severity: {pain_point.get('severity', 'Medium')}"
        ]

        # Main reason for priority
        if jtbd_score.opportunity_score > 15:
            why_top = f"Highly underserved customer need ({jtbd_score.opportunity_score}/20 opportunity score) affecting {rice_score.reach:,} users with strong evidence and feasible implementation."
        elif rice_score.rice_score > 1_000_000:
            why_top = f"Exceptional RICE score ({rice_score.rice_score:,.0f}) indicates massive value delivery potential with {rice_score.reach:,} users affected."
        else:
            why_top = f"Strong combination of customer need (JTBD: {jtbd_score.opportunity_score}/20) and strategic value (RICE: {rice_score.rice_score:,.0f})."

        # Quote samples
        quote_samples = [pain_point.get('quote', 'User feedback from research')]

        return Justification(
            why_top_priority=why_top,
            evidence=evidence,
            market_data=market_data,
            quote_samples=quote_samples
        )
