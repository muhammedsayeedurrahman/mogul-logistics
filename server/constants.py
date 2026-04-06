"""Single source of truth for shared constants across the codebase."""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Action costs (deducted from budget each step)
# ---------------------------------------------------------------------------
ACTION_COSTS: dict[str, float] = {
    "investigate": 50.0,
    "contact_carrier": 100.0,
    "escalate": 200.0,
    "file_claim": 300.0,
    "reschedule": 800.0,
    "approve_refund": 1500.0,
    "reroute": 2000.0,
    "split_shipment": 2500.0,
}

# ---------------------------------------------------------------------------
# How much progress each action contributes toward resolution
# ---------------------------------------------------------------------------
ACTION_PROGRESS: dict[str, float] = {
    "investigate": 0.15,
    "contact_carrier": 0.10,
    "escalate": 0.20,
    "reroute": 0.40,
    "reschedule": 0.35,
    "file_claim": 0.30,
    "approve_refund": 0.50,
    "split_shipment": 0.45,
}

# ---------------------------------------------------------------------------
# Valid action types (derived from ACTION_COSTS)
# ---------------------------------------------------------------------------
VALID_ACTIONS: set[str] = set(ACTION_COSTS.keys())

# ---------------------------------------------------------------------------
# Actions that can trigger full resolution (progress >= 1.0)
# ---------------------------------------------------------------------------
RESOLUTION_ACTIONS: set[str] = {
    "reroute",
    "reschedule",
    "file_claim",
    "approve_refund",
    "split_shipment",
}

# ---------------------------------------------------------------------------
# Priority ranking (lower = more urgent)
# ---------------------------------------------------------------------------
PRIORITY_RANK: dict[str, int] = {
    "critical": 0,
    "high": 1,
    "medium": 2,
    "low": 3,
}
