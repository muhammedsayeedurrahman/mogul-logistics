"""Typed EnvClient for MOGUL Logistics.

Provides a strongly-typed async client that converts between
ShipmentAction/ShipmentObservation/ShipmentState and the JSON
wire format expected by the OpenEnv server.

Example (async):
    >>> async with MogulLogisticsEnv(base_url="http://localhost:8000") as env:
    ...     result = await env.reset(task_id="task_easy")
    ...     while not result.done:
    ...         action = ShipmentAction(
    ...             action_type="investigate",
    ...             target_shipment_id="SHP-001",
    ...         )
    ...         result = await env.step(action)

Example (sync):
    >>> env = MogulLogisticsEnv(base_url="http://localhost:8000").sync()
    >>> with env:
    ...     result = env.reset(task_id="task_easy")
"""

from __future__ import annotations

from typing import Any, Dict

from openenv.core.env_client import EnvClient, StepResult

try:
    from .models import ShipmentAction, ShipmentObservation, ShipmentState
except ImportError:
    from models import ShipmentAction, ShipmentObservation, ShipmentState


class MogulLogisticsEnv(
    EnvClient[ShipmentAction, ShipmentObservation, ShipmentState]
):
    """Typed client for the MOGUL Logistics shipment exception environment.

    Translates between typed Pydantic models and the JSON wire protocol
    used by the OpenEnv server.
    """

    def _step_payload(self, action: ShipmentAction) -> Dict[str, Any]:
        """Convert a ShipmentAction to the JSON payload for the server."""
        return action.model_dump(mode="json")

    def _parse_result(self, payload: Dict[str, Any]) -> StepResult[ShipmentObservation]:
        """Parse a server JSON response into a typed StepResult."""
        observation = ShipmentObservation.model_validate(payload)
        return StepResult(
            observation=observation,
            reward=observation.reward,
            done=observation.done,
        )

    def _parse_state(self, payload: Dict[str, Any]) -> ShipmentState:
        """Parse a server state response into a typed ShipmentState."""
        return ShipmentState.model_validate(payload)
