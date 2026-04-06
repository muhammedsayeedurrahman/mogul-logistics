"""Tests for Pydantic data models."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from models import ShipmentAction, ShipmentObservation, ShipmentState


class TestShipmentAction:
    def test_valid_action(self):
        action = ShipmentAction(
            action_type="investigate",
            target_shipment_id="SHP-001",
            parameters={},
        )
        assert action.action_type == "investigate"
        assert action.target_shipment_id == "SHP-001"
        assert action.parameters == {}

    def test_invalid_action_type_rejected(self):
        with pytest.raises(ValidationError):
            ShipmentAction(
                action_type="fly_to_moon",
                target_shipment_id="SHP-001",
            )

    def test_invalid_shipment_id_rejected(self):
        with pytest.raises(ValidationError):
            ShipmentAction(
                action_type="investigate",
                target_shipment_id="SHP-999",
            )

    def test_string_parameters_parsed(self):
        action = ShipmentAction(
            action_type="escalate",
            target_shipment_id="SHP-001",
            parameters='{"reason": "urgent"}',
        )
        assert action.parameters == {"reason": "urgent"}

    def test_empty_string_parameters_default_to_dict(self):
        action = ShipmentAction(
            action_type="investigate",
            target_shipment_id="SHP-001",
            parameters="",
        )
        assert action.parameters == {}

    def test_whitespace_string_parameters_default_to_dict(self):
        action = ShipmentAction(
            action_type="investigate",
            target_shipment_id="SHP-001",
            parameters="   ",
        )
        assert action.parameters == {}

    def test_invalid_json_parameters_raises_error(self):
        with pytest.raises(ValidationError, match="Invalid JSON"):
            ShipmentAction(
                action_type="investigate",
                target_shipment_id="SHP-001",
                parameters="not valid json",
            )

    def test_default_parameters(self):
        action = ShipmentAction(
            action_type="investigate",
            target_shipment_id="SHP-001",
        )
        assert action.parameters == {}

    def test_all_valid_action_types(self):
        valid_types = [
            "investigate", "contact_carrier", "escalate", "file_claim",
            "reschedule", "approve_refund", "reroute", "split_shipment",
        ]
        for atype in valid_types:
            action = ShipmentAction(
                action_type=atype, target_shipment_id="SHP-001",
            )
            assert action.action_type == atype

    def test_all_valid_shipment_ids(self):
        for i in range(1, 9):
            sid = f"SHP-{i:03d}"
            action = ShipmentAction(
                action_type="investigate", target_shipment_id=sid,
            )
            assert action.target_shipment_id == sid


class TestShipmentObservation:
    def test_default_values(self):
        obs = ShipmentObservation()
        assert obs.shipment_status == ""
        assert obs.available_actions == []
        assert obs.budget_remaining == 0.0
        assert obs.done is False

    def test_custom_values(self):
        obs = ShipmentObservation(
            shipment_status="SHP-001: active",
            budget_remaining=5000.0,
            time_remaining=10,
            done=True,
            reward=0.85,
        )
        assert obs.budget_remaining == 5000.0
        assert obs.done is True
        assert obs.reward == 0.85


class TestShipmentState:
    def test_default_values(self):
        state = ShipmentState(episode_id="test")
        assert state.task_id == ""
        assert state.max_steps == 10
        assert state.total_exceptions == 0
        assert state.resolved_exceptions == 0
        assert state.total_cost_incurred == 0.0
        assert state.sla_violations == 0
        assert state.budget == 0.0

    def test_custom_values(self):
        state = ShipmentState(
            episode_id="ep-123",
            task_id="task_hard",
            max_steps=15,
            total_exceptions=8,
            resolved_exceptions=3,
            total_cost_incurred=5000.0,
            sla_violations=2,
            budget=10000.0,
        )
        assert state.task_id == "task_hard"
        assert state.resolved_exceptions == 3
