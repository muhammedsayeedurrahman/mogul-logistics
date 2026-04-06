"""Tests for grading logic."""

from __future__ import annotations

import pytest

from server.constants import ACTION_COSTS
from server.graders import action_cost, compute_decision_quality, grade_episode
from server.scenarios import Scenario, Shipment


class TestActionCost:
    def test_known_actions_return_correct_cost(self):
        assert action_cost("investigate") == 50.0
        assert action_cost("reroute") == 2000.0
        assert action_cost("split_shipment") == 2500.0

    def test_unknown_action_raises_value_error(self):
        with pytest.raises(ValueError, match="Unknown action type"):
            action_cost("nonexistent_action")

    def test_all_actions_have_costs(self):
        for action_type in ACTION_COSTS:
            cost = action_cost(action_type)
            assert cost > 0
            assert cost == ACTION_COSTS[action_type]


class TestComputeDecisionQuality:
    def test_empty_history_returns_zero(self):
        assert compute_decision_quality([], []) == 0.0

    def test_investigating_first_gives_high_score(self, sample_actions):
        ships = [
            Shipment(
                shipment_id="SHP-001", origin="A", destination="B",
                exception_type="weather_delay", priority="high",
                sla_deadline_steps=5,
            ),
            Shipment(
                shipment_id="SHP-002", origin="C", destination="D",
                exception_type="customs_hold", priority="medium",
                sla_deadline_steps=6,
            ),
        ]
        score = compute_decision_quality(sample_actions, ships)
        assert 0.0 <= score <= 1.0
        assert score > 0.5  # Good decisions: investigated first

    def test_not_investigating_penalized(self):
        from models import ShipmentAction

        actions = [
            ShipmentAction(
                action_type="reroute", target_shipment_id="SHP-001",
            ),
        ]
        ships = [
            Shipment(
                shipment_id="SHP-001", origin="A", destination="B",
                exception_type="weather_delay", priority="high",
                sla_deadline_steps=5,
            ),
        ]
        score = compute_decision_quality(actions, ships)
        assert 0.0 <= score <= 1.0
        # Penalized for not investigating
        assert score < 0.7


class TestGradeEpisode:
    def test_returns_float_in_valid_range(
        self, sample_state, easy_scenario, sample_actions,
    ):
        score = grade_episode(sample_state, easy_scenario, sample_actions)
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

    def test_perfect_episode_scores_high(self):
        from models import ShipmentAction, ShipmentState

        state = ShipmentState(
            episode_id="test",
            total_exceptions=1,
            resolved_exceptions=1,
            total_cost_incurred=50.0,
            sla_violations=0,
            budget=4950.0,
        )
        scenario = Scenario(
            shipments=[
                Shipment(
                    shipment_id="SHP-001", origin="A", destination="B",
                    exception_type="weather_delay", priority="high",
                    sla_deadline_steps=5,
                ),
            ],
            total_budget=5000.0,
        )
        actions = [
            ShipmentAction(
                action_type="investigate", target_shipment_id="SHP-001",
            ),
        ]
        score = grade_episode(state, scenario, actions)
        assert score >= 0.7  # All resolved + low cost + no SLA violations

    def test_zero_resolutions_scores_low(self, easy_scenario):
        from models import ShipmentState

        state = ShipmentState(
            episode_id="test",
            total_exceptions=1,
            resolved_exceptions=0,
            total_cost_incurred=5000.0,
            sla_violations=1,
            budget=0.0,
        )
        score = grade_episode(state, easy_scenario, [])
        assert score < 0.3

    def test_all_sla_violated_reduces_score(self, easy_scenario):
        from models import ShipmentAction, ShipmentState

        state = ShipmentState(
            episode_id="test",
            total_exceptions=1,
            resolved_exceptions=1,
            total_cost_incurred=100.0,
            sla_violations=1,
            budget=4900.0,
        )
        actions = [
            ShipmentAction(
                action_type="investigate", target_shipment_id="SHP-001",
            ),
        ]
        score = grade_episode(state, easy_scenario, actions)
        # SLA violation reduces score by up to 0.2
        assert score < 0.85
