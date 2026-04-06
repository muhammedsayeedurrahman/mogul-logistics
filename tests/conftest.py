"""Shared test fixtures for MOGUL Logistics tests."""

from __future__ import annotations

import pytest

from models import ShipmentAction, ShipmentState
from server.environment import ShipmentEnvironment
from server.scenarios import (
    Scenario,
    Shipment,
    generate_easy_scenario,
    generate_hard_scenario,
    generate_medium_scenario,
)


@pytest.fixture
def env():
    """Fresh ShipmentEnvironment instance."""
    return ShipmentEnvironment()


@pytest.fixture
def easy_env(env):
    """Environment reset to easy task."""
    env.reset(seed=42, task_id="task_easy")
    return env


@pytest.fixture
def medium_env(env):
    """Environment reset to medium task."""
    env.reset(seed=42, task_id="task_medium")
    return env


@pytest.fixture
def hard_env(env):
    """Environment reset to hard task."""
    env.reset(seed=42, task_id="task_hard")
    return env


@pytest.fixture
def easy_scenario():
    """Deterministic easy scenario."""
    return generate_easy_scenario(seed=42)


@pytest.fixture
def medium_scenario():
    """Deterministic medium scenario."""
    return generate_medium_scenario(seed=42)


@pytest.fixture
def hard_scenario():
    """Deterministic hard scenario."""
    return generate_hard_scenario(seed=42)


@pytest.fixture
def sample_state():
    """Sample ShipmentState for grading tests."""
    return ShipmentState(
        episode_id="test-ep",
        step_count=5,
        task_id="task_easy",
        max_steps=10,
        total_exceptions=4,
        resolved_exceptions=2,
        total_cost_incurred=3000.0,
        sla_violations=1,
        budget=9000.0,
    )


@pytest.fixture
def sample_actions():
    """Sample action sequence: investigate then resolve two shipments."""
    return [
        ShipmentAction(
            action_type="investigate", target_shipment_id="SHP-001",
        ),
        ShipmentAction(
            action_type="approve_refund", target_shipment_id="SHP-001",
        ),
        ShipmentAction(
            action_type="investigate", target_shipment_id="SHP-002",
        ),
        ShipmentAction(
            action_type="reschedule", target_shipment_id="SHP-002",
        ),
    ]
