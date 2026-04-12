"""Core environment — implements reset / step / state."""

from __future__ import annotations

from typing import Any, Optional
from uuid import uuid4

from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import EnvironmentMetadata

try:
    from ..models import ShipmentAction, ShipmentObservation, ShipmentState
except ImportError:
    from models import ShipmentAction, ShipmentObservation, ShipmentState
from server.constants import (
    ACTION_COSTS,
    ACTION_PROGRESS,
    RESOLUTION_ACTIONS,
    VALID_ACTIONS,
)
from server.graders import action_cost, grade_episode
from server.scenarios import SCENARIO_GENERATORS, Scenario, Shipment
from server.tasks import DEFAULT_TASK_ID, TASKS


class ShipmentEnvironment(
    Environment[ShipmentAction, ShipmentObservation, ShipmentState]
):
    """Logistics shipment exception resolution environment."""

    SUPPORTS_CONCURRENT_SESSIONS: bool = False

    def __init__(self) -> None:
        super().__init__()
        self._state = ShipmentState(episode_id=str(uuid4()))
        self._scenario: Scenario = Scenario()
        self._shipments: dict[str, Shipment] = {}
        self._actions_history: list[ShipmentAction] = []

    # ------------------------------------------------------------------
    # reset
    # ------------------------------------------------------------------

    def reset(
        self,
        seed: Optional[int] = None,
        episode_id: Optional[str] = None,
        **kwargs: Any,
    ) -> ShipmentObservation:
        task_id = kwargs.get("task_id", DEFAULT_TASK_ID)
        task_def = TASKS.get(task_id, TASKS[DEFAULT_TASK_ID])

        generator = SCENARIO_GENERATORS[task_def.scenario_key]
        self._scenario = generator(seed=seed)
        self._shipments = {s.shipment_id: s for s in self._scenario.shipments}
        self._actions_history = []

        self._state = ShipmentState(
            episode_id=episode_id or str(uuid4()),
            step_count=0,
            task_id=task_def.task_id,
            max_steps=task_def.max_steps,
            total_exceptions=len(self._scenario.shipments),
            resolved_exceptions=0,
            total_cost_incurred=0.0,
            sla_violations=0,
            budget=self._scenario.total_budget,
        )

        return self._build_observation(
            feedback=(
                f"Episode started - Task: {task_def.name} ({task_def.difficulty}). "
                f"{self._scenario.description}"
            ),
            done=False,
        )

    # ------------------------------------------------------------------
    # step
    # ------------------------------------------------------------------

    def step(
        self,
        action: ShipmentAction,
        timeout_s: Optional[float] = None,
        **kwargs: Any,
    ) -> ShipmentObservation:
        # Validate action type
        if action.action_type not in VALID_ACTIONS:
            return self._build_observation(
                feedback=(
                    f"[ERROR:INVALID_ACTION] '{action.action_type}' is not a valid "
                    f"action. Valid actions: {sorted(VALID_ACTIONS)}. "
                    f"Suggestion: start with 'investigate' to reveal exception details."
                ),
                done=False,
                reward=0.0,
            )

        # Validate target shipment
        shipment = self._shipments.get(action.target_shipment_id)
        if shipment is None:
            valid_ids = sorted(self._shipments.keys())
            return self._build_observation(
                feedback=(
                    f"[ERROR:INVALID_TARGET] Shipment '{action.target_shipment_id}' "
                    f"does not exist. Active shipments: {valid_ids}. "
                    f"Suggestion: check shipment_status field for available IDs."
                ),
                done=False,
                reward=0.0,
            )

        # Check budget
        cost = action_cost(action.action_type)
        if cost > self._state.budget:
            # Suggest cheaper alternatives
            affordable = sorted(
                [(a, c) for a, c in ACTION_COSTS.items() if c <= self._state.budget],
                key=lambda x: x[1],
            )
            suggestion = (
                f"Affordable actions: {', '.join(f'{a} (${int(c)})' for a, c in affordable)}"
                if affordable else "No actions are affordable."
            )
            return self._build_observation(
                feedback=(
                    f"[ERROR:BUDGET_EXCEEDED] '{action.action_type}' costs "
                    f"${cost:,.0f} but only ${self._state.budget:,.0f} remains. "
                    f"{suggestion}"
                ),
                done=False,
                reward=0.0,
            )

        # Check if already resolved
        if shipment.status == "resolved":
            active = [
                s.shipment_id for s in self._shipments.values()
                if s.status not in ("resolved", "failed")
            ]
            suggestion = (
                f"Active shipments needing attention: {active}"
                if active else "All shipments are resolved or failed."
            )
            return self._build_observation(
                feedback=(
                    f"[ERROR:ALREADY_RESOLVED] {shipment.shipment_id} is already "
                    f"resolved. {suggestion}"
                ),
                done=False,
                reward=0.0,
            )

        # ---- Process the action ----
        self._state.step_count += 1
        self._state.total_cost_incurred += cost
        self._state.budget -= cost
        self._actions_history.append(action)

        feedback = self._process_action(action, shipment)

        # Append cost/budget info to feedback
        feedback += (
            f" [Cost: ${cost:,.0f} | Budget remaining: "
            f"${self._state.budget:,.0f}]"
        )

        # Decrement SLA deadlines and check violations
        self._tick_sla()

        # Check termination
        all_resolved = all(
            s.status in ("resolved", "failed") for s in self._shipments.values()
        )
        out_of_steps = self._state.step_count >= self._state.max_steps
        out_of_budget = self._state.budget <= 0

        done = all_resolved or out_of_steps or out_of_budget

        # Compute reward
        reward = self._compute_step_reward(action, shipment)
        if done:
            reward = grade_episode(
                self._state, self._scenario, self._actions_history
            )
            # Append score breakdown to feedback
            total = max(self._state.total_exceptions, 1)
            res_ratio = self._state.resolved_exceptions / total
            max_b = max(self._scenario.total_budget, 1.0)
            cost_ratio = 1.0 - (self._state.total_cost_incurred / max_b)
            sla_ratio = 1.0 - (self._state.sla_violations / total)
            feedback += (
                f"\n--- EPISODE COMPLETE ---"
                f"\nFinal Score: {reward:.4f}"
                f"\n  Resolution: {self._state.resolved_exceptions}/{total}"
                f" ({res_ratio:.0%}) -> {res_ratio * 0.4:.4f}/0.40"
                f"\n  Cost Efficiency: ${self._state.total_cost_incurred:,.0f}"
                f"/${self._scenario.total_budget:,.0f}"
                f" -> {max(0, cost_ratio) * 0.25:.4f}/0.25"
                f"\n  SLA Compliance: {self._state.sla_violations} violations"
                f" -> {max(0, sla_ratio) * 0.2:.4f}/0.20"
                f"\n  Decision Quality: -> {reward - res_ratio * 0.4 - max(0, cost_ratio) * 0.25 - max(0, sla_ratio) * 0.2:.4f}/0.15"
            )

        return self._build_observation(feedback=feedback, done=done, reward=reward)

    # ------------------------------------------------------------------
    # state
    # ------------------------------------------------------------------

    @property
    def state(self) -> ShipmentState:
        return self._state

    def get_metadata(self) -> EnvironmentMetadata:
        return EnvironmentMetadata(
            name="MOGUL Logistics",
            description=(
                "Shipment exception resolution environment for RL training. "
                "An LLM agent triages and resolves logistics exceptions "
                "(delays, damages, misroutes, customs holds) across 3 difficulty "
                "levels with weighted grading on resolution rate, cost efficiency, "
                "SLA compliance, and decision quality."
            ),
            version="1.0.0",
            author="Muhammed Sayeedur Rahman",
        )

    # ------------------------------------------------------------------
    # internal helpers
    # ------------------------------------------------------------------

    def _process_action(
        self, action: ShipmentAction, shipment: Shipment
    ) -> str:
        atype = action.action_type
        sid = shipment.shipment_id

        # Investigate
        if atype == "investigate":
            shipment.investigated = True
            shipment.status = "investigating"
            progress = ACTION_PROGRESS["investigate"]
            shipment.resolution_progress = round(
                min(1.0, shipment.resolution_progress + progress), 4
            )
            return (
                f"[{sid}] Investigation complete. Exception: {shipment.exception_type}. "
                f"Priority: {shipment.priority}. {shipment.description}"
            )

        # Contact carrier
        if atype == "contact_carrier":
            progress = ACTION_PROGRESS["contact_carrier"]
            shipment.resolution_progress = round(
                min(1.0, shipment.resolution_progress + progress), 4
            )
            return (
                f"[{sid}] Contacted carrier {shipment.carrier}. "
                "They acknowledged the issue and will provide an update."
            )

        # Escalate
        if atype == "escalate":
            progress = ACTION_PROGRESS["escalate"]
            shipment.resolution_progress = round(
                min(1.0, shipment.resolution_progress + progress), 4
            )
            reason = action.parameters.get("reason", "urgent resolution needed")
            return (
                f"[{sid}] Escalated to management: '{reason}'. "
                "Expedited review initiated."
            )

        # Precondition: must investigate before costly resolution actions
        if not shipment.investigated and atype in RESOLUTION_ACTIONS:
            return (
                f"[{sid}] [ERROR:NOT_INVESTIGATED] Cannot '{atype}' without "
                f"investigating first. Use 'investigate' on {sid} before "
                f"resolution actions ({', '.join(sorted(RESOLUTION_ACTIONS))}). "
                f"Non-resolution actions (investigate, contact_carrier, escalate) "
                f"can be used without investigation."
            )

        # Resolution actions
        shipment.status = "action_taken"
        progress = ACTION_PROGRESS.get(atype, 0.2)
        shipment.resolution_progress = round(
            min(1.0, shipment.resolution_progress + progress), 4
        )

        # Check if fully resolved
        if shipment.resolution_progress >= 1.0:
            shipment.status = "resolved"
            shipment.resolution_progress = 1.0
            self._state.resolved_exceptions += 1
            return f"[{sid}] RESOLVED via '{atype}'. Exception cleared."

        return (
            f"[{sid}] Action '{atype}' applied. "
            f"Progress: {shipment.resolution_progress:.0%}. "
            "Further action may be needed."
        )

    def _tick_sla(self) -> None:
        """Decrement SLA countdown and record violations."""
        for s in self._shipments.values():
            if s.status in ("resolved", "failed"):
                continue
            s.sla_deadline_steps -= 1
            if s.sla_deadline_steps <= 0 and s.status != "resolved":
                self._state.sla_violations += 1
                s.status = "failed"

    def _compute_step_reward(
        self, action: ShipmentAction, shipment: Shipment
    ) -> float:
        """Small intermediate reward signal."""
        if shipment.status == "resolved":
            return 0.3
        if action.action_type == "investigate":
            return 0.05
        if shipment.resolution_progress > 0:
            return 0.1 * shipment.resolution_progress
        return 0.0

    def close(self) -> None:
        """Clean up environment resources."""
        self._shipments.clear()
        self._actions_history.clear()

    def _build_observation(
        self,
        feedback: str,
        done: bool,
        reward: float | None = None,
    ) -> ShipmentObservation:
        # Build status summary
        lines: list[str] = []
        for s in self._shipments.values():
            lines.append(
                f"  {s.shipment_id}: {s.exception_type} | "
                f"status={s.status} | priority={s.priority} | "
                f"progress={s.resolution_progress:.0%} | "
                f"SLA in {max(0, s.sla_deadline_steps)} steps"
            )
        status_text = "\n".join(lines) if lines else "No active shipments."

        # Exception details
        active = [s for s in self._shipments.values() if s.status not in ("resolved", "failed")]
        details_parts = [s.description for s in active]
        details_text = " | ".join(details_parts) if details_parts else "All exceptions handled."

        # Available actions
        available = sorted(VALID_ACTIONS)

        # Resolution progress map
        progress_map = {
            s.shipment_id: round(s.resolution_progress, 4)
            for s in self._shipments.values()
        }

        return ShipmentObservation(
            shipment_status=status_text,
            exception_details=details_text,
            available_actions=available,
            budget_remaining=round(self._state.budget, 2),
            time_remaining=max(0, self._state.max_steps - self._state.step_count),
            resolution_progress=progress_map,
            feedback=feedback,
            done=done,
            reward=reward,
        )
