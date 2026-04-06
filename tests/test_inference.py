"""Tests for the heuristic planner and observation parsing."""

from __future__ import annotations

from server.constants import ACTION_COSTS, VALID_ACTIONS
from server.heuristic import HeuristicPlanner, make_action, parse_shipments


class TestParseShipments:
    def test_parses_single_shipment(self):
        text = "  SHP-001: weather_delay | status=new | priority=high | progress=0% | SLA in 4 steps"
        ships = parse_shipments(text)
        assert len(ships) == 1
        assert ships[0]["id"] == "SHP-001"
        assert ships[0]["status"] == "new"
        assert ships[0]["priority"] == "high"
        assert ships[0]["progress"] == 0.0
        assert ships[0]["sla"] == 4

    def test_parses_multiple_shipments(self):
        text = (
            "  SHP-001: customs_hold | status=investigating | priority=critical | progress=15% | SLA in 2 steps\n"
            "  SHP-002: damage_reported | status=new | priority=high | progress=0% | SLA in 5 steps\n"
            "  SHP-003: weather_delay | status=resolved | priority=medium | progress=100% | SLA in 3 steps"
        )
        ships = parse_shipments(text)
        assert len(ships) == 3
        assert ships[0]["progress"] == 0.15
        assert ships[2]["status"] == "resolved"
        assert ships[2]["progress"] == 1.0

    def test_empty_text_returns_empty(self):
        assert parse_shipments("") == []
        assert parse_shipments("No active shipments.") == []


class TestMakeAction:
    def test_creates_well_formed_action(self):
        action = make_action("investigate", "SHP-001")
        assert action["action_type"] == "investigate"
        assert action["target_shipment_id"] == "SHP-001"
        assert action["parameters"] == {}


class TestHeuristicPlanner:
    def _make_obs(
        self,
        ships_text: str,
        budget: float = 5000,
        time_left: int = 5,
    ) -> dict:
        return {
            "shipment_status": ships_text,
            "budget_remaining": budget,
            "time_remaining": time_left,
        }

    def test_investigate_first_on_new_shipment(self):
        planner = HeuristicPlanner()
        obs = self._make_obs(
            "  SHP-001: weather_delay | status=new | priority=high | progress=0% | SLA in 4 steps"
        )
        action, explanation = planner.pick_action(obs)
        assert action["action_type"] == "investigate"
        assert action["target_shipment_id"] == "SHP-001"

    def test_continues_resolution_after_investigate(self):
        planner = HeuristicPlanner()
        # After investigation (15% progress)
        obs = self._make_obs(
            "  SHP-001: weather_delay | status=investigating | priority=high | progress=15% | SLA in 3 steps"
        )
        action, explanation = planner.pick_action(obs)
        # Should take a resolution action, not investigate again
        assert action["action_type"] != "investigate"
        assert action["target_shipment_id"] == "SHP-001"

    def test_returns_explanation_string(self):
        planner = HeuristicPlanner()
        obs = self._make_obs(
            "  SHP-001: weather_delay | status=new | priority=high | progress=0% | SLA in 4 steps"
        )
        action, explanation = planner.pick_action(obs)
        assert isinstance(explanation, str)
        assert len(explanation) > 0

    def test_handles_empty_observation(self):
        planner = HeuristicPlanner()
        obs = self._make_obs("")
        action, explanation = planner.pick_action(obs)
        assert action["action_type"] in VALID_ACTIONS

    def test_dq_farming_when_plan_exhausted(self):
        planner = HeuristicPlanner()
        # All resolved except one uninvestigated
        obs = self._make_obs(
            "  SHP-001: weather_delay | status=resolved | priority=high | progress=100% | SLA in 0 steps\n"
            "  SHP-002: customs_hold | status=new | priority=medium | progress=0% | SLA in 1 steps",
            budget=100,
            time_left=2,
        )
        action, explanation = planner.pick_action(obs)
        # Should investigate SHP-002 for DQ points
        assert action["action_type"] == "investigate"
        assert action["target_shipment_id"] == "SHP-002"

    def test_prioritizes_tight_sla(self):
        planner = HeuristicPlanner()
        obs = self._make_obs(
            "  SHP-001: weather_delay | status=new | priority=medium | progress=0% | SLA in 6 steps\n"
            "  SHP-002: customs_hold | status=new | priority=high | progress=0% | SLA in 3 steps",
            budget=10000,
            time_left=10,
        )
        action, explanation = planner.pick_action(obs)
        # Should work on SHP-002 first (tighter SLA)
        assert action["target_shipment_id"] == "SHP-002"

    def test_produces_valid_actions_only(self):
        planner = HeuristicPlanner()
        obs = self._make_obs(
            "  SHP-001: weather_delay | status=new | priority=high | progress=0% | SLA in 4 steps",
        )
        for _ in range(10):
            action, _ = planner.pick_action(obs)
            assert action["action_type"] in VALID_ACTIONS
            assert action["target_shipment_id"].startswith("SHP-")

    def test_full_resolution_sequence(self):
        """Simulate a full easy episode through the planner."""
        planner = HeuristicPlanner()
        budget = 5000
        sla = 4

        # Step 1: new ship
        obs = self._make_obs(
            f"  SHP-001: weather_delay | status=new | priority=high | progress=0% | SLA in {sla} steps",
            budget=budget,
        )
        a1, _ = planner.pick_action(obs)
        assert a1["action_type"] == "investigate"
        budget -= ACTION_COSTS["investigate"]
        sla -= 1

        # Step 2: after investigate
        obs = self._make_obs(
            f"  SHP-001: weather_delay | status=investigating | priority=high | progress=15% | SLA in {sla} steps",
            budget=budget,
        )
        a2, _ = planner.pick_action(obs)
        assert a2["action_type"] in VALID_ACTIONS
        budget -= ACTION_COSTS[a2["action_type"]]
        sla -= 1

        # Step 3: higher progress
        progress = 15 + int(
            {
                "approve_refund": 50,
                "escalate": 20,
                "reschedule": 35,
            }.get(a2["action_type"], 30)
        )
        obs = self._make_obs(
            f"  SHP-001: weather_delay | status=action_taken | priority=high | progress={progress}% | SLA in {sla} steps",
            budget=budget,
        )
        a3, _ = planner.pick_action(obs)
        assert a3["action_type"] in VALID_ACTIONS
