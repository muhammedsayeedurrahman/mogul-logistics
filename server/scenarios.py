"""Shipment scenario generator for different difficulty levels."""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Literal


ExceptionType = Literal[
    "weather_delay",
    "customs_hold",
    "damage_reported",
    "misroute",
    "carrier_breakdown",
    "port_closure",
    "documentation_error",
    "capacity_overflow",
]

ShipmentStatus = Literal[
    "new",
    "investigating",
    "action_taken",
    "resolved",
    "failed",
]

Priority = Literal["critical", "high", "medium", "low"]


@dataclass
class Shipment:
    """A single shipment with an exception."""

    shipment_id: str
    origin: str
    destination: str
    exception_type: ExceptionType
    priority: Priority
    sla_deadline_steps: int  # steps until SLA is breached
    status: ShipmentStatus = "new"
    investigated: bool = False
    resolution_progress: float = 0.0
    resolution_cost: float = 0.0
    description: str = ""
    carrier: str = ""
    value: float = 0.0


@dataclass
class Scenario:
    """A complete scenario with shipments and budget."""

    shipments: list[Shipment] = field(default_factory=list)
    total_budget: float = 0.0
    max_steps: int = 10
    description: str = ""


_CITIES = [
    "Shanghai", "Rotterdam", "Los Angeles", "Singapore", "Dubai",
    "Mumbai", "Hamburg", "Tokyo", "New York", "Busan",
]

_CARRIERS = [
    "Maersk", "MSC", "CMA CGM", "COSCO", "Hapag-Lloyd",
    "Evergreen", "ONE", "Yang Ming", "HMM", "ZIM",
]


def _rand_pair(rng: random.Random) -> tuple[str, str]:
    a, b = rng.sample(_CITIES, 2)
    return a, b


def generate_easy_scenario(seed: int | None = None) -> Scenario:
    """Single delayed shipment — straightforward resolution."""
    rng = random.Random(seed)
    origin, dest = _rand_pair(rng)
    carrier = rng.choice(_CARRIERS)
    value = round(rng.uniform(5_000, 25_000), 2)

    shipment = Shipment(
        shipment_id="SHP-001",
        origin=origin,
        destination=dest,
        exception_type="weather_delay",
        priority=rng.choice(["high", "medium"]),
        sla_deadline_steps=4,
        description=(
            f"Shipment SHP-001 from {origin} to {dest} via {carrier} is delayed "
            f"due to severe weather. Cargo value: ${value:,.2f}. "
            "The vessel is currently held at port awaiting clearance. "
            "Expected delay: 2-4 days. Customer has been notified but is requesting updates."
        ),
        carrier=carrier,
        value=value,
    )

    return Scenario(
        shipments=[shipment],
        total_budget=5_000.0,
        max_steps=5,
        description=(
            "A single shipment has been delayed due to weather conditions. "
            "Investigate the cause and determine the best resolution."
        ),
    )


def generate_medium_scenario(seed: int | None = None) -> Scenario:
    """Multiple exceptions requiring triage and prioritization."""
    rng = random.Random(seed)
    exception_configs: list[tuple[ExceptionType, Priority, int, str]] = [
        ("customs_hold", "critical", 3, "held at customs due to incomplete documentation"),
        ("damage_reported", "high", 5, "container damage reported during transit"),
        ("weather_delay", "medium", 6, "delayed due to tropical storm warning"),
        ("misroute", "high", 4, "incorrectly routed to wrong distribution center"),
    ]

    shipments = []
    for i, (exc_type, prio, sla, desc_suffix) in enumerate(exception_configs, start=1):
        origin, dest = _rand_pair(rng)
        carrier = rng.choice(_CARRIERS)
        value = round(rng.uniform(8_000, 60_000), 2)
        sid = f"SHP-{i:03d}"
        shipments.append(
            Shipment(
                shipment_id=sid,
                origin=origin,
                destination=dest,
                exception_type=exc_type,
                priority=prio,
                sla_deadline_steps=sla,
                description=(
                    f"Shipment {sid} ({origin} → {dest}) via {carrier}: "
                    f"{desc_suffix}. Cargo value: ${value:,.2f}."
                ),
                carrier=carrier,
                value=value,
            )
        )

    return Scenario(
        shipments=shipments,
        total_budget=12_000.0,
        max_steps=10,
        description=(
            "Multiple shipments have different exception types. "
            "Prioritize by SLA urgency and resolve each appropriately within budget."
        ),
    )


def generate_hard_scenario(seed: int | None = None) -> Scenario:
    """Cascading supply chain disruption with tight budget."""
    rng = random.Random(seed)

    # Port closure affects multiple shipments
    closed_port = rng.choice(["Shanghai", "Rotterdam", "Singapore"])

    exception_configs: list[tuple[ExceptionType, Priority, int, str]] = [
        ("port_closure", "critical", 2, f"stuck at {closed_port} port closure"),
        ("port_closure", "critical", 3, f"rerouting needed due to {closed_port} closure"),
        ("capacity_overflow", "high", 4, "overflow from rerouted vessels"),
        ("customs_hold", "high", 4, "expedited customs review triggered"),
        ("damage_reported", "medium", 6, "container shifted during emergency reroute"),
        ("carrier_breakdown", "medium", 5, "backup carrier vehicle breakdown"),
        ("documentation_error", "low", 7, "paperwork mismatch from rush reroute"),
        ("misroute", "low", 8, "sent to wrong hub during disruption"),
    ]

    shipments = []
    for i, (exc_type, prio, sla, desc_suffix) in enumerate(exception_configs, start=1):
        origin, dest = _rand_pair(rng)
        carrier = rng.choice(_CARRIERS)
        value = round(rng.uniform(10_000, 150_000), 2)
        sid = f"SHP-{i:03d}"
        shipments.append(
            Shipment(
                shipment_id=sid,
                origin=origin,
                destination=dest,
                exception_type=exc_type,
                priority=prio,
                sla_deadline_steps=sla,
                description=(
                    f"Shipment {sid} ({origin} → {dest}) via {carrier}: "
                    f"{desc_suffix}. Cargo value: ${value:,.2f}."
                ),
                carrier=carrier,
                value=value,
            )
        )

    return Scenario(
        shipments=shipments,
        total_budget=15_000.0,
        max_steps=15,
        description=(
            f"Major port closure at {closed_port} has caused cascading failures "
            "across 8 shipments. Budget is limited — you must triage and minimize "
            "total loss. Not all shipments can be fully resolved."
        ),
    )


SCENARIO_GENERATORS = {
    "easy": generate_easy_scenario,
    "medium": generate_medium_scenario,
    "hard": generate_hard_scenario,
}
