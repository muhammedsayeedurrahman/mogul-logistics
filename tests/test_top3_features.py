"""Tests for TOP 3 features: Multi-Agent Negotiation, Constraints Viz, Explainable AI."""

import pytest
from server.multi_agent import (
    CarrierAgent,
    CustomsAgent,
    WarehouseAgent,
    NegotiationEngine,
)
from server.constraints_viz import (
    render_budget_constraint,
    render_time_constraint,
    render_sla_constraints,
    render_active_constraints,
)
from server.explainable_ai import ExplainableAI
from models import ShipmentAction


# ── Multi-Agent Negotiation Tests ───────────────────────────────────


def test_carrier_agent_proposes_solution():
    """Carrier agent generates valid proposals."""
    agent = CarrierAgent()
    shipment = {
        "tracking_id": "SHP-001",
        "sla_deadline_hours": 12,  # Tight SLA
        "exception_type": "customs_hold",
        "priority": "critical"
    }
    context = {"budget_remaining": 5000, "time_remaining": 10}

    proposal = agent.propose_solution(shipment, context)

    assert proposal.agent_name == "CarrierAgent"
    assert proposal.action.target_shipment_id == "SHP-001"
    assert isinstance(proposal.score, float)
    assert 0 <= proposal.score <= 1
    assert proposal.reasoning
    assert "cost" in proposal.trade_offs


def test_customs_agent_prioritizes_compliance():
    """Customs agent prioritizes compliance over cost."""
    agent = CustomsAgent()
    shipment = {
        "tracking_id": "SHP-002",
        "sla_deadline_hours": 48,
        "exception_type": "customs_hold",
        "priority": "standard"
    }
    context = {"budget_remaining": 5000, "time_remaining": 20}

    proposal = agent.propose_solution(shipment, context)

    assert proposal.agent_name == "CustomsAgent"
    assert proposal.action.action_type == "escalate"  # Compliance-focused
    assert proposal.trade_offs["compliance"] > 0.8  # High compliance score


def test_warehouse_agent_maximizes_throughput():
    """Warehouse agent optimizes for throughput."""
    agent = WarehouseAgent()
    shipment = {
        "tracking_id": "SHP-003",
        "sla_deadline_hours": 10,  # Critical
        "exception_type": "documentation_missing",
        "priority": "critical"
    }
    context = {"budget_remaining": 3000, "time_remaining": 5}

    proposal = agent.propose_solution(shipment, context)

    assert proposal.agent_name == "WarehouseAgent"
    assert "throughput" in proposal.trade_offs


def test_negotiation_engine_reaches_consensus():
    """Negotiation engine coordinates multiple agents."""
    engine = NegotiationEngine()
    shipment = {
        "tracking_id": "SHP-004",
        "sla_deadline_hours": 16,
        "exception_type": "port_closure",
        "priority": "standard"
    }
    context = {"budget_remaining": 4000, "time_remaining": 15}

    action, metadata = engine.negotiate_action(shipment, context)

    assert isinstance(action, ShipmentAction)
    assert action.target_shipment_id == "SHP-004"
    assert "proposals" in metadata
    assert len(metadata["proposals"]) == 3  # All 3 agents
    assert "consensus" in metadata
    assert metadata["consensus"]["winner"] in ["CarrierAgent", "CustomsAgent", "WarehouseAgent"]
    assert "disagreement_level" in metadata
    assert 0 <= metadata["disagreement_level"] <= 1


# ── Constraints Visualization Tests ─────────────────────────────────


def test_render_budget_constraint():
    """Budget constraint renders with progress bar."""
    html = render_budget_constraint(
        budget_remaining=3000,
        budget_initial=5000,
        steps_taken=5
    )

    assert "Budget Constraint" in html
    assert "3,000" in html or "3000" in html
    assert "5,000" in html or "5000" in html
    assert "40.0%" in html  # Usage percentage


def test_render_time_constraint():
    """Time constraint renders countdown."""
    html = render_time_constraint(
        time_remaining=10,
        time_initial=20
    )

    assert "Time Constraint" in html
    assert "10" in html
    assert "20" in html
    assert "50.0%" in html  # Usage percentage


def test_render_sla_constraints_color_zones():
    """SLA constraints use color-coded urgency zones."""
    shipments = [
        {"tracking_id": "SHP-001", "sla_deadline_hours": 8, "status": "in_transit"},   # Red
        {"tracking_id": "SHP-002", "sla_deadline_hours": 20, "status": "customs"},     # Orange
        {"tracking_id": "SHP-003", "sla_deadline_hours": 60, "status": "delivered"}    # Green
    ]

    html = render_sla_constraints(shipments)

    assert "SHP-001" in html
    assert "SHP-002" in html
    assert "SHP-003" in html
    assert "#f44336" in html  # Red for critical
    assert "#FF9800" in html  # Orange for warning


def test_render_active_constraints_identifies_binding():
    """Active constraints identifies which are binding."""
    obs = {
        "budget_remaining": 500,  # Critical
        "time_remaining": 2,      # Critical
        "shipments": [
            {"tracking_id": "SHP-001", "sla_deadline_hours": 10}
        ]
    }

    html = render_active_constraints(obs)

    assert "Budget Constraint" in html or "budget" in html.lower()
    assert "Time Constraint" in html or "time" in html.lower()
    assert "CRITICAL" in html


def test_render_active_constraints_all_satisfied():
    """Active constraints shows green when all satisfied."""
    obs = {
        "budget_remaining": 4000,
        "time_remaining": 15,
        "shipments": [
            {"tracking_id": "SHP-001", "sla_deadline_hours": 48}
        ]
    }

    html = render_active_constraints(obs)

    assert "All Constraints Satisfied" in html or "✅" in html


# ── Explainable AI Tests ────────────────────────────────────────────


def test_explainable_ai_generates_reasoning_chain():
    """Explainable AI generates step-by-step reasoning."""
    explainer = ExplainableAI()
    action = ShipmentAction(
        action_type="investigate",
        target_shipment_id="SHP-001",
        parameters={}
    )
    shipment = {
        "tracking_id": "SHP-001",
        "sla_deadline_hours": 30,
        "exception_type": "documentation_missing",
        "priority": "standard"
    }
    context = {"budget_remaining": 4500, "time_remaining": 18}

    explanation = explainer.explain_action(action, shipment, context)

    assert explanation.chosen_action == action
    assert len(explanation.reasoning_chain) > 0
    assert all(isinstance(step, str) for step in explanation.reasoning_chain)


def test_explainable_ai_provides_alternatives():
    """Explainable AI generates alternative actions."""
    explainer = ExplainableAI()
    action = ShipmentAction(
        action_type="escalate",
        target_shipment_id="SHP-002",
        parameters={}
    )
    shipment = {
        "tracking_id": "SHP-002",
        "sla_deadline_hours": 8,
        "exception_type": "customs_hold",
        "priority": "critical"
    }
    context = {"budget_remaining": 2000, "time_remaining": 5}

    explanation = explainer.explain_action(action, shipment, context)

    assert len(explanation.alternatives) > 0
    for alt in explanation.alternatives:
        assert alt.action_type != action.action_type  # Different from chosen
        assert isinstance(alt.score, float)
        assert len(alt.pros) > 0
        assert len(alt.cons) > 0


def test_explainable_ai_analyzes_trade_offs():
    """Explainable AI analyzes trade-offs."""
    explainer = ExplainableAI()
    action = ShipmentAction(
        action_type="reroute",
        target_shipment_id="SHP-003",
        parameters={}
    )
    shipment = {
        "tracking_id": "SHP-003",
        "sla_deadline_hours": 24,
        "exception_type": "port_closure",
        "priority": "standard"
    }
    context = {"budget_remaining": 3000, "time_remaining": 10}

    explanation = explainer.explain_action(action, shipment, context)

    assert "cost_efficiency" in explanation.trade_offs
    assert "speed" in explanation.trade_offs
    assert "risk_mitigation" in explanation.trade_offs
    assert "compliance" in explanation.trade_offs
    assert all(0 <= v <= 1 for v in explanation.trade_offs.values())


def test_explainable_ai_calculates_confidence():
    """Explainable AI calculates confidence score."""
    explainer = ExplainableAI()
    action = ShipmentAction(
        action_type="investigate",
        target_shipment_id="SHP-004",
        parameters={}
    )
    shipment = {
        "tracking_id": "SHP-004",
        "sla_deadline_hours": 72,  # Lots of time
        "exception_type": "unknown",
        "priority": "standard"
    }
    context = {"budget_remaining": 5000, "time_remaining": 20}

    explanation = explainer.explain_action(action, shipment, context)

    assert 0 <= explanation.confidence <= 1
    assert explanation.confidence > 0.5  # Should be confident in investigate with lots of time


def test_explainable_ai_provides_counterfactual():
    """Explainable AI generates counterfactual explanation."""
    explainer = ExplainableAI()
    action = ShipmentAction(
        action_type="escalate",
        target_shipment_id="SHP-005",
        parameters={}
    )
    shipment = {
        "tracking_id": "SHP-005",
        "sla_deadline_hours": 6,
        "exception_type": "customs_hold",
        "priority": "critical"
    }
    context = {"budget_remaining": 1500, "time_remaining": 3}

    explanation = explainer.explain_action(action, shipment, context)

    assert explanation.counterfactual
    assert "If we had chosen" in explanation.counterfactual or "instead" in explanation.counterfactual


def test_explainable_ai_identifies_decision_factors():
    """Explainable AI identifies key decision factors."""
    explainer = ExplainableAI()
    action = ShipmentAction(
        action_type="investigate",
        target_shipment_id="SHP-006",
        parameters={}
    )
    shipment = {
        "tracking_id": "SHP-006",
        "sla_deadline_hours": 40,
        "exception_type": "documentation_missing",
        "priority": "standard"
    }
    context = {"budget_remaining": 4000, "time_remaining": 15}

    explanation = explainer.explain_action(action, shipment, context)

    assert len(explanation.decision_factors) > 0
    for factor_name, weight, impact in explanation.decision_factors:
        assert isinstance(factor_name, str)
        assert 0 <= weight <= 1
        assert isinstance(impact, str)
