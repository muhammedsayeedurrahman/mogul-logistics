"""Task definitions with difficulty progression."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TaskDefinition:
    """Immutable task configuration."""

    task_id: str
    name: str
    difficulty: str  # easy | medium | hard
    description: str
    max_steps: int
    scenario_key: str  # key into SCENARIO_GENERATORS


TASKS: dict[str, TaskDefinition] = {
    "task_easy": TaskDefinition(
        task_id="task_easy",
        name="Single Delayed Shipment",
        difficulty="easy",
        description=(
            "One shipment with a weather delay. Investigate the cause, "
            "decide to reroute or wait, and confirm resolution. "
            "Generous budget, 5 steps max."
        ),
        max_steps=5,
        scenario_key="easy",
    ),
    "task_medium": TaskDefinition(
        task_id="task_medium",
        name="Multi-Exception Triage",
        difficulty="medium",
        description=(
            "3-4 shipments with different exception types (delay, damage, "
            "customs hold, misroute). Prioritize by SLA urgency and resolve "
            "each appropriately. 10 steps, moderate budget."
        ),
        max_steps=10,
        scenario_key="medium",
    ),
    "task_hard": TaskDefinition(
        task_id="task_hard",
        name="Supply Chain Disruption",
        difficulty="hard",
        description=(
            "6-8 shipments with cascading failures from a port closure. "
            "Limited budget forces triage decisions. Some shipments cannot "
            "be fully resolved — minimize total loss. 15 steps, tight budget."
        ),
        max_steps=15,
        scenario_key="hard",
    ),
}

DEFAULT_TASK_ID = "task_easy"
