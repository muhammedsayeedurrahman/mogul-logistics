"""Grading logic — returns diverse scores in 0.0-1.0 range."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from server.scenarios import Scenario, Shipment

    from models import ShipmentAction, ShipmentState


# ---------------------------------------------------------------------------
# Action costs (deducted from budget)
# ---------------------------------------------------------------------------
ACTION_COSTS: dict[str, float] = {
    "investigate": 50.0,
    "reroute": 2000.0,
    "escalate": 200.0,
    "reschedule": 800.0,
    "file_claim": 300.0,
    "contact_carrier": 100.0,
    "approve_refund": 1500.0,
    "split_shipment": 2500.0,
}


def action_cost(action_type: str) -> float:
    """Return the cost of an action type."""
    return ACTION_COSTS.get(action_type, 100.0)


# ---------------------------------------------------------------------------
# Decision quality heuristics
# ---------------------------------------------------------------------------

def compute_decision_quality(
    actions_history: list[ShipmentAction],
    shipments: list[Shipment],
) -> float:
    """Score 0.0-1.0 for how well the agent made decisions.

    Rewards:
    - Investigating before taking costly actions (+)
    - Acting on higher-priority shipments first (+)
    - Penalizes acting without investigation (-)
    """
    if not actions_history:
        return 0.0

    investigated_ids: set[str] = set()
    acted_without_investigation = 0
    priority_order_score = 0.0
    total_actions = 0

    priority_rank = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    shipment_priority = {s.shipment_id: s.priority for s in shipments}

    last_priority_rank = -1

    for action in actions_history:
        total_actions += 1
        sid = action.target_shipment_id

        if action.action_type == "investigate":
            investigated_ids.add(sid)
        elif sid not in investigated_ids and action.action_type not in ("escalate", "contact_carrier"):
            acted_without_investigation += 1

        prio = shipment_priority.get(sid, "low")
        rank = priority_rank.get(prio, 3)
        if rank <= last_priority_rank or last_priority_rank == -1:
            priority_order_score += 1.0
        last_priority_rank = rank

    if total_actions == 0:
        return 0.0

    investigation_ratio = 1.0 - (acted_without_investigation / total_actions)
    priority_ratio = priority_order_score / total_actions

    return round(0.6 * investigation_ratio + 0.4 * priority_ratio, 4)


# ---------------------------------------------------------------------------
# Main grader
# ---------------------------------------------------------------------------

def grade_episode(
    state: ShipmentState,
    scenario: Scenario,
    actions_history: list[ShipmentAction],
) -> float:
    """Grade an episode — returns a float in [0.0, 1.0].

    Components (weights):
        Resolution rate:    40%
        Cost efficiency:    25%
        SLA compliance:     20%
        Decision quality:   15%
    """
    total = max(state.total_exceptions, 1)

    # Component 1: Resolution rate (0.0 - 0.4)
    resolution_ratio = state.resolved_exceptions / total
    resolution_score = resolution_ratio * 0.4

    # Component 2: Cost efficiency (0.0 - 0.25)
    max_budget = max(scenario.total_budget, 1.0)
    cost_ratio = 1.0 - (state.total_cost_incurred / max_budget)
    cost_score = max(0.0, cost_ratio) * 0.25

    # Component 3: SLA compliance (0.0 - 0.2)
    sla_ratio = 1.0 - (state.sla_violations / total)
    sla_score = max(0.0, sla_ratio) * 0.2

    # Component 4: Decision quality (0.0 - 0.15)
    dq = compute_decision_quality(actions_history, scenario.shipments)
    dq_score = dq * 0.15

    score = resolution_score + cost_score + sla_score + dq_score
    return round(min(1.0, max(0.0, score)), 4)
