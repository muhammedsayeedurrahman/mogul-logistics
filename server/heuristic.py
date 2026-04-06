"""Shared heuristic planner for the MOGUL Logistics environment.

Used by both inference.py (LLM fallback) and gradio_custom.py (demo mode).
"""

from __future__ import annotations

import re
from itertools import permutations

from .constants import (
    ACTION_COSTS,
    ACTION_PROGRESS,
    PRIORITY_RANK,
    RESOLUTION_ACTIONS,
)

# ---------------------------------------------------------------------------
# Observation parser
# ---------------------------------------------------------------------------

SHIP_RE = re.compile(
    r"(SHP-\d+):\s+\S+\s+\|\s+status=(\w+)\s+\|\s+priority=(\w+)"
    r"\s+\|\s+progress=(\d+)%\s+\|\s+SLA in (\d+) steps"
)


def parse_shipments(status_text: str) -> list[dict]:
    """Parse shipment status text into structured dicts."""
    ships: list[dict] = []
    for m in SHIP_RE.finditer(status_text):
        ships.append({
            "id": m.group(1),
            "status": m.group(2),
            "priority": m.group(3),
            "progress": int(m.group(4)) / 100.0,
            "sla": int(m.group(5)),
        })
    return ships


def make_action(atype: str, sid: str) -> dict:
    """Create a well-formed action dict."""
    return {"action_type": atype, "target_shipment_id": sid, "parameters": {}}


# ---------------------------------------------------------------------------
# Planning helpers
# ---------------------------------------------------------------------------

def _min_steps_to_resolve(progress: float, investigated: bool) -> int:
    if progress >= 0.50 and investigated:
        return 1
    if investigated:
        return 2
    return 3


def _cheap_path_remaining_cost(
    progress: float, investigated: bool, sla: int,
) -> int:
    """Return cheapest remaining cost considering both 3-step and 4-step paths."""
    if not investigated:
        fast = (
            ACTION_COSTS["investigate"]
            + ACTION_COSTS["approve_refund"]
            + ACTION_COSTS["reschedule"]
        )
        cheap = (
            ACTION_COSTS["investigate"]
            + ACTION_COSTS["escalate"]
            + ACTION_COSTS["file_claim"]
            + ACTION_COSTS["reschedule"]
        )
        return int(cheap if sla >= 4 else fast)
    if progress >= 0.50:
        return int(ACTION_COSTS["reschedule"])
    fast = ACTION_COSTS["approve_refund"] + ACTION_COSTS["reschedule"]
    cheap = (
        ACTION_COSTS["escalate"]
        + ACTION_COSTS["file_claim"]
        + ACTION_COSTS["reschedule"]
    )
    return int(cheap if sla >= 3 else fast)


def _plan_resolution_order(
    ships: list[dict], total_steps: int, budget: int,
) -> list[str]:
    """Find the ordering of salvageable ships that maximizes resolutions."""
    candidates = []
    for s in ships:
        if s["status"] in ("resolved", "failed"):
            continue
        investigated = (
            s["progress"] >= 0.14
            or s["status"] in ("investigating", "action_taken")
        )
        steps_needed = _min_steps_to_resolve(s["progress"], investigated)
        cost_needed = _cheap_path_remaining_cost(
            s["progress"], investigated, s["sla"],
        )
        candidates.append({
            **s,
            "investigated": investigated,
            "steps_needed": steps_needed,
            "cost_needed": cost_needed,
        })

    if not candidates:
        return []

    potentially_salvageable = [
        c for c in candidates if c["sla"] >= c["steps_needed"]
    ]

    if not potentially_salvageable:
        candidates.sort(key=lambda s: PRIORITY_RANK.get(s["priority"], 3))
        return [c["id"] for c in candidates]

    if len(potentially_salvageable) <= 6:
        best_order: list[str] = []
        best_count = 0

        for perm in permutations(potentially_salvageable):
            elapsed = 0
            cost_used = 0
            resolved_count = 0
            order: list[str] = []

            for ship in perm:
                steps_needed = ship["steps_needed"]
                effective_sla = ship["sla"] - elapsed
                cost_needed = ship["cost_needed"]

                if (
                    effective_sla >= steps_needed
                    and (cost_used + cost_needed) <= budget
                ):
                    resolved_count += 1
                    elapsed += steps_needed
                    cost_used += cost_needed
                    order.append(ship["id"])

                if elapsed >= total_steps:
                    break

            if resolved_count > best_count:
                best_count = resolved_count
                best_order = order

        return best_order
    else:
        potentially_salvageable.sort(
            key=lambda s: (s["sla"] - s["steps_needed"], s["steps_needed"])
        )
        order: list[str] = []
        elapsed = 0
        cost_used = 0
        for ship in potentially_salvageable:
            effective_sla = ship["sla"] - elapsed
            if (
                effective_sla >= ship["steps_needed"]
                and (cost_used + ship["cost_needed"]) <= budget
            ):
                order.append(ship["id"])
                elapsed += ship["steps_needed"]
                cost_used += ship["cost_needed"]
        return order


# ---------------------------------------------------------------------------
# Stateful heuristic planner
# ---------------------------------------------------------------------------

class HeuristicPlanner:
    """Tracks resolution plan across steps and picks optimal actions.

    Returns (action_dict, explanation_string) from pick_action().
    """

    def __init__(self) -> None:
        self.plan: list[str] = []
        self.plan_idx: int = 0
        self.resolved_ids: set[str] = set()
        self.investigated_ids: set[str] = set()
        self.dq_investigated: set[str] = set()

    def pick_action(self, observation: dict) -> tuple[dict, str]:
        """Pick the next action based on current observation.

        Returns:
            (action_dict, explanation_string)
        """
        status_text = observation.get("shipment_status", "")
        budget = observation.get("budget_remaining", 0)
        time_left = observation.get("time_remaining", 0)

        ships = parse_shipments(status_text)
        if not ships:
            return (
                make_action("investigate", "SHP-001"),
                "No shipments parsed — investigating SHP-001",
            )

        ship_map = {s["id"]: s for s in ships}

        for s in ships:
            if s["status"] == "resolved":
                self.resolved_ids.add(s["id"])

        active = [
            s for s in ships if s["status"] not in ("resolved", "failed")
        ]

        if not self.plan or self.plan_idx >= len(self.plan):
            self.plan = _plan_resolution_order(active, time_left, budget)
            self.plan_idx = 0

        while (
            self.plan_idx < len(self.plan)
            and self.plan[self.plan_idx] in self.resolved_ids
        ):
            self.plan_idx += 1

        if self.plan_idx < len(self.plan):
            target_id = self.plan[self.plan_idx]
            target = ship_map.get(target_id)
            if target and target["status"] == "failed":
                self.plan_idx += 1

        if self.plan_idx >= len(self.plan):
            return self._dq_farm(ships, budget, time_left)

        target_id = self.plan[self.plan_idx]
        target = ship_map.get(target_id)

        if not target or target["status"] in ("resolved", "failed"):
            self.plan_idx += 1
            return self._dq_farm(ships, budget, time_left)

        return self._resolve_ship(target, budget)

    def _resolve_ship(
        self, target: dict, budget: float,
    ) -> tuple[dict, str]:
        sid = target["id"]
        prog = target["progress"]
        investigated = (
            prog >= 0.14
            or target["status"] in ("investigating", "action_taken")
            or sid in self.investigated_ids
        )

        if not investigated and prog < 0.001:
            if budget >= ACTION_COSTS["investigate"]:
                self.investigated_ids.add(sid)
                return (
                    make_action("investigate", sid),
                    f"Investigating {sid} first (required before resolution)",
                )

        if prog >= 0.14:
            self.investigated_ids.add(sid)
            investigated = True

        needed = 1.0 - prog
        if investigated:
            finishing = []
            for atype in RESOLUTION_ACTIONS:
                if (
                    ACTION_PROGRESS[atype] >= needed
                    and ACTION_COSTS[atype] <= budget
                ):
                    finishing.append((atype, ACTION_COSTS[atype]))
            if finishing:
                finishing.sort(key=lambda x: x[1])
                atype = finishing[0][0]
                return (
                    make_action(atype, sid),
                    (
                        f"{atype} will finish {sid} "
                        f"({ACTION_PROGRESS[atype]:.0%} >= {needed:.0%} needed)"
                    ),
                )

        if investigated and target["sla"] >= 3:
            cheap_remaining = (
                ACTION_COSTS["escalate"]
                + ACTION_COSTS["file_claim"]
                + ACTION_COSTS["reschedule"]
            )
            if prog < 0.20 and budget >= cheap_remaining:
                return (
                    make_action("escalate", sid),
                    (
                        f"Escalating {sid} (cheap path: $1,300 remaining "
                        f"vs $2,300 fast path, SLA={target['sla']})"
                    ),
                )
            if 0.20 <= prog < 0.40 and budget >= (
                ACTION_COSTS["file_claim"] + ACTION_COSTS["reschedule"]
            ):
                return (
                    make_action("file_claim", sid),
                    f"Filing claim for {sid} (cheap path, progress={prog:.0%})",
                )

        if investigated:
            if prog < 0.50 and budget >= ACTION_COSTS["approve_refund"]:
                return (
                    make_action("approve_refund", sid),
                    f"Approve refund for {sid} (fast path, adds 50% progress)",
                )
            if budget >= ACTION_COSTS["reschedule"]:
                return (
                    make_action("reschedule", sid),
                    f"Rescheduling {sid} (adds 35% progress)",
                )

        if not investigated and budget >= ACTION_COSTS["investigate"]:
            self.investigated_ids.add(sid)
            return (
                make_action("investigate", sid),
                f"Must investigate {sid} before resolution actions",
            )

        return (
            make_action("contact_carrier", sid),
            f"Low budget — contacting carrier for {sid}",
        )

    def _dq_farm(
        self, ships: list[dict], budget: float, time_left: int,
    ) -> tuple[dict, str]:
        """Use remaining steps for DQ points by investigating priority-first."""
        uninvestigated = [
            s for s in ships
            if s["status"] not in ("resolved",)
            and s["id"] not in self.investigated_ids
            and s["id"] not in self.dq_investigated
            and s["progress"] < 0.001
        ]

        uninvestigated.sort(
            key=lambda s: PRIORITY_RANK.get(s["priority"], 3)
        )

        for s in uninvestigated:
            if budget >= ACTION_COSTS["investigate"]:
                self.dq_investigated.add(s["id"])
                self.investigated_ids.add(s["id"])
                return (
                    make_action("investigate", s["id"]),
                    (
                        f"DQ farming: investigating {s['id']} "
                        f"({s['priority']}) for decision quality points"
                    ),
                )

        active = [
            s for s in ships if s["status"] not in ("resolved", "failed")
        ]
        if active:
            active.sort(key=lambda s: PRIORITY_RANK.get(s["priority"], 3))
            sid = active[0]["id"]
            if budget >= ACTION_COSTS["contact_carrier"]:
                return (
                    make_action("contact_carrier", sid),
                    f"All ships investigated — contacting carrier for {sid}",
                )
            return (
                make_action("investigate", sid),
                f"Budget depleted — attempting investigation on {sid}",
            )

        return (
            make_action("investigate", "SHP-001"),
            "No active ships — fallback action",
        )
