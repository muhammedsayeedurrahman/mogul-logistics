"""Multi-Agent Negotiation System for MOGUL Logistics.

Simulates negotiation between different stakeholders:
- CarrierAgent: Optimizes for fuel cost and vehicle utilization
- CustomsAgent: Prioritizes compliance and documentation
- WarehouseAgent: Minimizes storage costs and maximizes throughput

Each agent proposes solutions, and a consensus mechanism selects the best option.
"""

from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from models import ShipmentAction
import random


@dataclass
class Proposal:
    """A proposed solution from an agent."""
    agent_name: str
    action: ShipmentAction
    score: float
    reasoning: str
    trade_offs: Dict[str, float]  # cost, time, compliance, risk


class CarrierAgent:
    """Optimizes for cost-effective routing and fuel efficiency."""

    def propose_solution(self, shipment: Dict[str, Any], context: Dict[str, Any]) -> Proposal:
        """Propose carrier-optimal solution."""
        shipment_id = shipment["tracking_id"]
        sla_remaining = shipment["sla_deadline_hours"]

        # Carrier prefers ground transport (cheap) unless SLA is tight
        if sla_remaining < 24:
            action_type = "escalate"
            reasoning = "SLA critical - expedite to avoid penalty"
            cost_score = 0.3  # Expensive
            time_score = 0.9  # Fast
        elif shipment["exception_type"] == "customs_hold":
            action_type = "escalate"
            reasoning = "Clear customs to resume transit"
            cost_score = 0.5
            time_score = 0.7
        else:
            action_type = "investigate"
            reasoning = "Gather information before committing resources"
            cost_score = 0.9  # Cheap
            time_score = 0.5  # Slow

        action = ShipmentAction(
            action_type=action_type,
            target_shipment_id=shipment_id,
            parameters={}
        )

        # Overall score = weighted average favoring cost
        score = 0.6 * cost_score + 0.3 * time_score + 0.1 * 0.8

        return Proposal(
            agent_name="CarrierAgent",
            action=action,
            score=score,
            reasoning=reasoning,
            trade_offs={
                "cost": cost_score,
                "time": time_score,
                "compliance": 0.8,
                "risk": 0.6
            }
        )


class CustomsAgent:
    """Prioritizes regulatory compliance and documentation."""

    def propose_solution(self, shipment: Dict[str, Any], context: Dict[str, Any]) -> Proposal:
        """Propose customs-optimal solution."""
        shipment_id = shipment["tracking_id"]
        exception_type = shipment["exception_type"]

        # Customs prioritizes compliance
        if exception_type == "customs_hold":
            action_type = "escalate"
            reasoning = "Regulatory compliance critical - expedite clearance"
            compliance_score = 1.0
            time_score = 0.8
        elif exception_type == "documentation_missing":
            action_type = "investigate"
            reasoning = "Verify documentation before proceeding"
            compliance_score = 0.9
            time_score = 0.4
        else:
            action_type = "investigate"
            reasoning = "Audit for compliance issues"
            compliance_score = 0.95
            time_score = 0.5

        action = ShipmentAction(
            action_type=action_type,
            target_shipment_id=shipment_id,
            parameters={}
        )

        # Overall score = weighted average favoring compliance
        score = 0.1 * 0.6 + 0.2 * time_score + 0.7 * compliance_score

        return Proposal(
            agent_name="CustomsAgent",
            action=action,
            score=score,
            reasoning=reasoning,
            trade_offs={
                "cost": 0.6,
                "time": time_score,
                "compliance": compliance_score,
                "risk": 0.3
            }
        )


class WarehouseAgent:
    """Minimizes storage costs and maximizes throughput."""

    def propose_solution(self, shipment: Dict[str, Any], context: Dict[str, Any]) -> Proposal:
        """Propose warehouse-optimal solution."""
        shipment_id = shipment["tracking_id"]
        priority = shipment.get("priority", "standard")
        sla_remaining = shipment["sla_deadline_hours"]

        # Warehouse wants to clear inventory quickly
        if sla_remaining < 12:
            action_type = "escalate"
            reasoning = "Free up warehouse space urgently"
            throughput_score = 1.0
            cost_score = 0.4
        elif priority == "critical":
            action_type = "escalate"
            reasoning = "High-priority shipment blocking other orders"
            throughput_score = 0.9
            cost_score = 0.5
        else:
            action_type = "investigate"
            reasoning = "Standard processing - gather info first"
            throughput_score = 0.6
            cost_score = 0.8

        action = ShipmentAction(
            action_type=action_type,
            target_shipment_id=shipment_id,
            parameters={}
        )

        # Overall score = weighted average favoring throughput
        score = 0.4 * cost_score + 0.5 * throughput_score + 0.1 * 0.7

        return Proposal(
            agent_name="WarehouseAgent",
            action=action,
            score=score,
            reasoning=reasoning,
            trade_offs={
                "cost": cost_score,
                "throughput": throughput_score,
                "compliance": 0.7,
                "risk": 0.5
            }
        )


class NegotiationEngine:
    """Coordinates multi-agent negotiation and consensus building."""

    def __init__(self):
        self.carrier_agent = CarrierAgent()
        self.customs_agent = CustomsAgent()
        self.warehouse_agent = WarehouseAgent()

    def negotiate_action(
        self,
        shipment: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Tuple[ShipmentAction, Dict[str, Any]]:
        """
        Run multi-agent negotiation to select best action.

        Returns:
            (selected_action, negotiation_metadata)
        """
        # Each agent proposes a solution
        proposals = [
            self.carrier_agent.propose_solution(shipment, context),
            self.customs_agent.propose_solution(shipment, context),
            self.warehouse_agent.propose_solution(shipment, context),
        ]

        # Consensus mechanism: highest score wins
        # (In real system, could be voting, weighted average, game theory)
        best_proposal = max(proposals, key=lambda p: p.score)

        # Metadata for visualization
        metadata = {
            "negotiation_rounds": 1,
            "proposals": [
                {
                    "agent": p.agent_name,
                    "action": p.action.action_type,
                    "score": round(p.score, 3),
                    "reasoning": p.reasoning,
                    "trade_offs": p.trade_offs,
                }
                for p in proposals
            ],
            "consensus": {
                "winner": best_proposal.agent_name,
                "action": best_proposal.action.action_type,
                "score": round(best_proposal.score, 3),
                "reasoning": best_proposal.reasoning,
            },
            "disagreement_level": round(
                max(p.score for p in proposals) - min(p.score for p in proposals),
                3
            ),
        }

        return best_proposal.action, metadata


# Global instance
negotiation_engine = NegotiationEngine()
