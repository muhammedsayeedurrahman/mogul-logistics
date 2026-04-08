"""Explainable AI system for MOGUL Logistics.

Provides comprehensive explanations for agent decisions:
- Why each action was chosen (reasoning chain)
- What alternatives were considered (counterfactuals)
- Trade-offs analyzed (cost vs time vs compliance)
- Confidence scores (uncertainty quantification)
- Decision tree visualization (logic flow)
"""

from typing import Dict, Any, List, Tuple
from dataclasses import dataclass
from models import ShipmentAction


@dataclass
class Alternative:
    """An alternative action that was considered."""
    action_type: str
    score: float
    pros: List[str]
    cons: List[str]
    outcome_forecast: str


@dataclass
class Explanation:
    """Complete explanation for a decision."""
    chosen_action: ShipmentAction
    reasoning_chain: List[str]
    alternatives: List[Alternative]
    trade_offs: Dict[str, float]
    confidence: float
    decision_factors: List[Tuple[str, float, str]]  # (factor, weight, impact)
    counterfactual: str  # "If we had done X instead, then Y would happen"


class ExplainableAI:
    """Generate human-understandable explanations for AI decisions."""

    def explain_action(
        self,
        action: ShipmentAction,
        shipment: Dict[str, Any],
        context: Dict[str, Any],
        negotiation_metadata: Dict[str, Any] = None
    ) -> Explanation:
        """
        Generate comprehensive explanation for why this action was chosen.

        Args:
            action: The selected action
            shipment: Shipment data
            context: Environment context
            negotiation_metadata: Multi-agent negotiation data (if available)

        Returns:
            Explanation object with reasoning, alternatives, trade-offs
        """
        # Extract key factors
        sla_hours = shipment.get("sla_deadline_hours", 0)
        exception = shipment.get("exception_type", "unknown")
        priority = shipment.get("priority", "standard")
        budget_remaining = context.get("budget_remaining", 0)
        time_remaining = context.get("time_remaining", 0)

        # Build reasoning chain
        reasoning_chain = self._build_reasoning_chain(
            action, shipment, context
        )

        # Generate alternatives
        alternatives = self._generate_alternatives(
            action, shipment, context
        )

        # Analyze trade-offs
        trade_offs = self._analyze_trade_offs(
            action, shipment, context
        )

        # Calculate confidence
        confidence = self._calculate_confidence(
            action, shipment, context, negotiation_metadata
        )

        # Identify decision factors
        decision_factors = self._identify_decision_factors(
            action, shipment, context
        )

        # Generate counterfactual
        counterfactual = self._generate_counterfactual(
            action, alternatives
        )

        return Explanation(
            chosen_action=action,
            reasoning_chain=reasoning_chain,
            alternatives=alternatives,
            trade_offs=trade_offs,
            confidence=confidence,
            decision_factors=decision_factors,
            counterfactual=counterfactual
        )

    def _build_reasoning_chain(
        self,
        action: ShipmentAction,
        shipment: Dict[str, Any],
        context: Dict[str, Any]
    ) -> List[str]:
        """Build step-by-step reasoning chain."""
        chain = []

        # Step 1: Situation assessment
        sla_hours = shipment.get("sla_deadline_hours", 0)
        exception = shipment.get("exception_type", "unknown")
        priority = shipment.get("priority", "standard")

        chain.append(f"📋 Situation: {exception} exception on {priority} priority shipment")

        # Step 2: Constraint analysis
        if sla_hours < 24:
            chain.append(f"⚠️ Constraint: Critical SLA deadline in {sla_hours:.0f} hours")
        else:
            chain.append(f"✓ Constraint: Comfortable SLA deadline ({sla_hours:.0f} hours)")

        # Step 3: Action selection logic
        if action.action_type == "investigate":
            chain.append("🔍 Decision: Investigate first to gather complete information")
            chain.append("💡 Rationale: Avoid costly mistakes by understanding root cause")
        elif action.action_type == "escalate":
            chain.append("⚡ Decision: Expedite customs clearance")
            chain.append("💡 Rationale: Remove blocking regulatory constraint quickly")
        elif action.action_type == "reroute":
            chain.append("🚚 Decision: Reroute shipment to alternative path")
            chain.append("💡 Rationale: Current route blocked or suboptimal")
        else:
            chain.append(f"Decision: {action.action_type}")

        # Step 4: Expected outcome
        budget_remaining = context.get("budget_remaining", 0)
        if action.action_type == "investigate":
            chain.append(f"📈 Expected outcome: Gain clarity, minimal cost (${budget_remaining - 200:,.0f} remaining)")
        elif action.action_type == "escalate":
            chain.append(f"📈 Expected outcome: Clear customs, resume transit (${budget_remaining - 800:,.0f} remaining)")

        return chain

    def _generate_alternatives(
        self,
        action: ShipmentAction,
        shipment: Dict[str, Any],
        context: Dict[str, Any]
    ) -> List[Alternative]:
        """Generate alternative actions that were considered."""
        alternatives = []

        # Alternative 1: Investigate (if not chosen)
        if action.action_type != "investigate":
            alternatives.append(Alternative(
                action_type="investigate",
                score=0.65,
                pros=["Low cost ($200)", "Gathers information", "Low risk"],
                cons=["Slow", "Doesn't directly resolve issue", "Consumes a step"],
                outcome_forecast="Gain clarity on root cause, but delay resolution by 1 step"
            ))

        # Alternative 2: Expedite customs (if not chosen)
        if action.action_type != "escalate":
            alternatives.append(Alternative(
                action_type="escalate",
                score=0.75,
                pros=["Fast resolution", "Removes blocker", "High compliance"],
                cons=["High cost ($800)", "May fail if docs incomplete", "Budget impact"],
                outcome_forecast="Clear customs in 1 step if documentation is correct"
            ))

        # Alternative 3: Reroute (if applicable)
        if action.action_type != "reroute" and shipment.get("exception_type") == "port_closure":
            alternatives.append(Alternative(
                action_type="reroute",
                score=0.70,
                pros=["Avoids closure", "Maintains timeline", "Flexible"],
                cons=["Moderate cost ($500)", "Route uncertainty", "May increase distance"],
                outcome_forecast="Bypass closure, but incur rerouting cost and potential delay"
            ))

        # Alternative 4: Wait (always an option)
        alternatives.append(Alternative(
            action_type="wait",
            score=0.30,
            pros=["Zero cost", "Preserve budget", "Wait for situation to resolve"],
            cons=["Time waste", "SLA risk", "Passive approach", "No progress"],
            outcome_forecast="Situation may resolve naturally, but SLA deadline approaches"
        ))

        return sorted(alternatives, key=lambda a: a.score, reverse=True)[:3]

    def _analyze_trade_offs(
        self,
        action: ShipmentAction,
        shipment: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, float]:
        """Analyze trade-offs for this action."""
        # Action costs
        action_costs = {
            "investigate": 200,
            "escalate": 800,
            "reroute": 500,
            "wait": 0
        }

        # Action speeds (0-1, higher = faster)
        action_speeds = {
            "investigate": 0.5,
            "escalate": 0.9,
            "reroute": 0.7,
            "wait": 0.1
        }

        # Action risks (0-1, higher = riskier)
        action_risks = {
            "investigate": 0.2,
            "escalate": 0.4,
            "reroute": 0.5,
            "wait": 0.8
        }

        action_type = action.action_type
        budget_remaining = context.get("budget_remaining", 5000)

        # Calculate normalized trade-offs
        cost_score = 1.0 - (action_costs.get(action_type, 500) / budget_remaining)
        speed_score = action_speeds.get(action_type, 0.5)
        risk_score = 1.0 - action_risks.get(action_type, 0.5)  # Invert risk
        compliance_score = 0.9 if action_type == "escalate" else 0.7

        return {
            "cost_efficiency": max(0, min(1, cost_score)),
            "speed": speed_score,
            "risk_mitigation": risk_score,
            "compliance": compliance_score,
        }

    def _calculate_confidence(
        self,
        action: ShipmentAction,
        shipment: Dict[str, Any],
        context: Dict[str, Any],
        negotiation_metadata: Dict[str, Any] = None
    ) -> float:
        """Calculate confidence score (0-1) for this decision."""
        confidence_factors = []

        # Factor 1: Multi-agent agreement
        if negotiation_metadata:
            disagreement = negotiation_metadata.get("disagreement_level", 0.5)
            agreement_conf = 1.0 - disagreement
            confidence_factors.append(agreement_conf)

        # Factor 2: SLA urgency clarity
        sla_hours = shipment.get("sla_deadline_hours", 0)
        if sla_hours < 12:
            # Very urgent = high confidence in expedite
            sla_conf = 0.95 if action.action_type == "escalate" else 0.6
        elif sla_hours > 48:
            # Lots of time = high confidence in investigate
            sla_conf = 0.95 if action.action_type == "investigate" else 0.7
        else:
            sla_conf = 0.75  # Medium confidence

        confidence_factors.append(sla_conf)

        # Factor 3: Budget adequacy
        budget_remaining = context.get("budget_remaining", 0)
        action_cost = {"investigate": 200, "escalate": 800, "reroute": 500}.get(action.action_type, 300)
        budget_conf = min(1.0, budget_remaining / (action_cost * 3))  # Can afford 3x this action?
        confidence_factors.append(budget_conf)

        # Overall confidence = geometric mean
        if confidence_factors:
            product = 1.0
            for cf in confidence_factors:
                product *= cf
            confidence = product ** (1.0 / len(confidence_factors))
        else:
            confidence = 0.75

        return round(confidence, 3)

    def _identify_decision_factors(
        self,
        action: ShipmentAction,
        shipment: Dict[str, Any],
        context: Dict[str, Any]
    ) -> List[Tuple[str, float, str]]:
        """Identify key factors that influenced the decision."""
        factors = []

        # Factor 1: SLA urgency
        sla_hours = shipment.get("sla_deadline_hours", 0)
        if sla_hours < 24:
            factors.append((
                "SLA Urgency",
                0.4,  # weight
                f"Critical deadline in {sla_hours:.0f}h drives expedited action"
            ))
        else:
            factors.append((
                "SLA Urgency",
                0.2,
                f"Comfortable deadline ({sla_hours:.0f}h) allows methodical approach"
            ))

        # Factor 2: Budget constraint
        budget_remaining = context.get("budget_remaining", 0)
        if budget_remaining < 1500:
            factors.append((
                "Budget Constraint",
                0.3,
                f"Low budget (${budget_remaining:,.0f}) favors cost-effective actions"
            ))
        else:
            factors.append((
                "Budget Constraint",
                0.15,
                f"Adequate budget (${budget_remaining:,.0f}) allows flexibility"
            ))

        # Factor 3: Exception type
        exception = shipment.get("exception_type", "unknown")
        if exception == "customs_hold":
            factors.append((
                "Exception Type",
                0.25,
                "Customs hold requires regulatory intervention"
            ))
        elif exception == "port_closure":
            factors.append((
                "Exception Type",
                0.25,
                "Port closure requires physical rerouting"
            ))
        else:
            factors.append((
                "Exception Type",
                0.2,
                f"{exception} requires investigation"
            ))

        # Factor 4: Priority
        priority = shipment.get("priority", "standard")
        if priority == "critical":
            factors.append((
                "Priority Level",
                0.2,
                "Critical priority demands fast resolution"
            ))
        else:
            factors.append((
                "Priority Level",
                0.1,
                "Standard priority allows balanced approach"
            ))

        # Sort by weight
        return sorted(factors, key=lambda f: f[1], reverse=True)

    def _generate_counterfactual(
        self,
        action: ShipmentAction,
        alternatives: List[Alternative]
    ) -> str:
        """Generate a counterfactual explanation."""
        if not alternatives:
            return "No alternative actions considered."

        best_alt = alternatives[0]

        if action.action_type == "investigate" and best_alt.action_type == "escalate":
            return (
                f"If we had chosen '{best_alt.action_type}' instead, we would resolve faster "
                f"but spend ${600} more. The investigation approach trades speed for cost efficiency "
                f"and information gathering."
            )
        elif action.action_type == "escalate" and best_alt.action_type == "investigate":
            return (
                f"If we had chosen '{best_alt.action_type}' instead, we would save ${600} "
                f"but risk SLA violation due to delayed resolution. The expedite approach "
                f"prioritizes deadline compliance over cost."
            )
        else:
            return (
                f"If we had chosen '{best_alt.action_type}' (score: {best_alt.score:.2f}) instead of "
                f"'{action.action_type}', the outcome would likely be: {best_alt.outcome_forecast}"
            )


# Global instance
explainable_ai = ExplainableAI()
