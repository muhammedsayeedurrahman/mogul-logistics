"""Tests for the ShipmentEnvironment."""

from __future__ import annotations

import pytest

from models import ShipmentAction


class TestReset:
    def test_reset_returns_observation(self, env):
        obs = env.reset(seed=42, task_id="task_easy")
        assert obs is not None
        assert obs.done is False
        assert obs.feedback != ""

    def test_reset_with_seed_is_deterministic(self, env):
        obs1 = env.reset(seed=123, task_id="task_easy")
        obs2 = env.reset(seed=123, task_id="task_easy")
        assert obs1.shipment_status == obs2.shipment_status
        assert obs1.budget_remaining == obs2.budget_remaining

    def test_reset_easy_has_one_shipment(self, easy_env):
        assert easy_env.state.total_exceptions == 1
        assert easy_env.state.budget == 5000.0
        assert easy_env.state.max_steps == 5

    def test_reset_medium_has_four_shipments(self, medium_env):
        assert medium_env.state.total_exceptions == 4
        assert medium_env.state.budget == 12000.0
        assert medium_env.state.max_steps == 10

    def test_reset_hard_has_eight_shipments(self, hard_env):
        assert hard_env.state.total_exceptions == 8
        assert hard_env.state.budget == 15000.0
        assert hard_env.state.max_steps == 15

    def test_reset_clears_previous_state(self, env):
        env.reset(seed=42, task_id="task_easy")
        action = ShipmentAction(
            action_type="investigate", target_shipment_id="SHP-001",
        )
        env.step(action)
        assert env.state.step_count == 1

        # Reset should clear everything
        env.reset(seed=42, task_id="task_easy")
        assert env.state.step_count == 0
        assert env.state.resolved_exceptions == 0


class TestStep:
    def test_valid_investigate_action(self, easy_env):
        action = ShipmentAction(
            action_type="investigate", target_shipment_id="SHP-001",
        )
        obs = easy_env.step(action)
        assert obs.done is False
        assert "Investigation complete" in obs.feedback
        assert easy_env.state.step_count == 1
        assert easy_env.state.total_cost_incurred == 50.0

    def test_invalid_action_type_returns_error(self, easy_env):
        action = ShipmentAction.__new__(ShipmentAction)
        object.__setattr__(action, "action_type", "fly_to_moon")
        object.__setattr__(action, "target_shipment_id", "SHP-001")
        object.__setattr__(action, "parameters", {})
        obs = easy_env.step(action)
        assert "INVALID_ACTION" in obs.feedback
        assert obs.reward == 0.0

    def test_invalid_target_returns_error(self, easy_env):
        action = ShipmentAction.__new__(ShipmentAction)
        object.__setattr__(action, "action_type", "investigate")
        object.__setattr__(action, "target_shipment_id", "SHP-999")
        object.__setattr__(action, "parameters", {})
        obs = easy_env.step(action)
        assert "INVALID_TARGET" in obs.feedback

    def test_budget_exceeded_returns_error(self, easy_env):
        # Drain budget first
        easy_env._state.budget = 10.0
        action = ShipmentAction(
            action_type="reroute", target_shipment_id="SHP-001",
        )
        obs = easy_env.step(action)
        assert "BUDGET_EXCEEDED" in obs.feedback

    def test_resolution_without_investigation_blocked(self, easy_env):
        action = ShipmentAction(
            action_type="reroute", target_shipment_id="SHP-001",
        )
        obs = easy_env.step(action)
        assert "NOT_INVESTIGATED" in obs.feedback

    def test_investigate_then_resolve_works(self, easy_env):
        # Investigate
        inv = ShipmentAction(
            action_type="investigate", target_shipment_id="SHP-001",
        )
        easy_env.step(inv)

        # Approve refund (50% progress)
        refund = ShipmentAction(
            action_type="approve_refund", target_shipment_id="SHP-001",
        )
        easy_env.step(refund)

        # Reschedule (35% + 50% + 15% = 100%)
        resched = ShipmentAction(
            action_type="reschedule", target_shipment_id="SHP-001",
        )
        obs = easy_env.step(resched)

        assert obs.done is True
        assert obs.reward is not None
        assert obs.reward > 0.5
        assert easy_env.state.resolved_exceptions == 1


class TestSLA:
    def test_sla_ticks_down_each_step(self, easy_env):
        # Get initial SLA from shipment
        initial_sla = easy_env._shipments["SHP-001"].sla_deadline_steps

        action = ShipmentAction(
            action_type="investigate", target_shipment_id="SHP-001",
        )
        easy_env.step(action)

        current_sla = easy_env._shipments["SHP-001"].sla_deadline_steps
        assert current_sla == initial_sla - 1

    def test_sla_violation_recorded(self, env):
        env.reset(seed=42, task_id="task_easy")
        # Force SLA to 1 step
        env._shipments["SHP-001"].sla_deadline_steps = 1

        action = ShipmentAction(
            action_type="investigate", target_shipment_id="SHP-001",
        )
        env.step(action)
        # After step, SLA decrements to 0 -> violation
        assert env.state.sla_violations == 1


class TestTermination:
    def test_terminates_when_all_resolved(self, easy_env):
        inv = ShipmentAction(
            action_type="investigate", target_shipment_id="SHP-001",
        )
        easy_env.step(inv)

        refund = ShipmentAction(
            action_type="approve_refund", target_shipment_id="SHP-001",
        )
        easy_env.step(refund)

        resched = ShipmentAction(
            action_type="reschedule", target_shipment_id="SHP-001",
        )
        obs = easy_env.step(resched)
        assert obs.done is True

    def test_terminates_when_out_of_steps(self, easy_env):
        easy_env._state.max_steps = 1
        action = ShipmentAction(
            action_type="investigate", target_shipment_id="SHP-001",
        )
        obs = easy_env.step(action)
        assert obs.done is True

    def test_terminates_when_out_of_budget(self, easy_env):
        easy_env._state.budget = 50.0
        action = ShipmentAction(
            action_type="investigate", target_shipment_id="SHP-001",
        )
        obs = easy_env.step(action)
        assert obs.done is True  # Budget now 0


class TestClose:
    def test_close_cleans_up(self, easy_env):
        easy_env.close()
        assert len(easy_env._shipments) == 0
        assert len(easy_env._actions_history) == 0
