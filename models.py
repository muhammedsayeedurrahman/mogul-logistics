"""Data models for the Shipment Exception Resolution environment."""

from __future__ import annotations

import json
from typing import Any, Literal

from openenv.core.env_server.types import Action, Observation, State
from pydantic import Field, field_validator


ActionType = Literal[
    "investigate",
    "contact_carrier",
    "escalate",
    "file_claim",
    "reschedule",
    "approve_refund",
    "reroute",
    "split_shipment",
]

ShipmentId = Literal[
    "SHP-001",
    "SHP-002",
    "SHP-003",
    "SHP-004",
    "SHP-005",
    "SHP-006",
    "SHP-007",
    "SHP-008",
]


class ShipmentAction(Action):
    """An action the agent can take to resolve shipment exceptions."""

    action_type: ActionType = Field(
        ...,
        description="Type of action to resolve the shipment exception",
    )
    target_shipment_id: ShipmentId = Field(
        ...,
        description="Target shipment to act on",
    )
    parameters: dict[str, Any] = Field(
        default_factory=dict,
        description='JSON parameters, e.g. {} or {"reason": "urgent"}',
    )

    @field_validator("parameters", mode="before")
    @classmethod
    def _parse_parameters(cls, v: Any) -> dict[str, Any]:
        """Accept JSON strings from the Gradio web UI."""
        if isinstance(v, str):
            v = v.strip()
            if not v:
                return {}
            return json.loads(v)
        return v


class ShipmentObservation(Observation):
    """What the agent observes after each action."""

    shipment_status: str = Field(
        default="", description="Summary of all active shipment statuses"
    )
    exception_details: str = Field(
        default="", description="Text description of current exceptions"
    )
    available_actions: list[str] = Field(
        default_factory=list, description="Valid actions the agent can take"
    )
    budget_remaining: float = Field(
        default=0.0, description="Resolution budget remaining"
    )
    time_remaining: int = Field(
        default=0, description="Steps remaining in the episode"
    )
    resolution_progress: dict[str, float] = Field(
        default_factory=dict,
        description="Per-exception progress (0.0 to 1.0)",
    )
    feedback: str = Field(
        default="", description="Result / feedback from last action"
    )


class ShipmentState(State):
    """Episode metadata tracked across steps."""

    task_id: str = Field(default="")
    max_steps: int = Field(default=10)
    total_exceptions: int = Field(default=0)
    resolved_exceptions: int = Field(default=0)
    total_cost_incurred: float = Field(default=0.0)
    sla_violations: int = Field(default=0)
    budget: float = Field(default=0.0)
