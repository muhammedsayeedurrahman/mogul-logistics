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
    "Mumbai", "Delhi NCR", "Chennai", "Bangalore", "Kolkata",
    "Hyderabad", "Pune", "Ahmedabad", "Jaipur", "Lucknow",
]

_CARRIERS = [
    "Blue Dart", "DTDC", "Delhivery", "Gati", "Ecom Express",
    "Rivigo", "SafeXpress", "TCI Express", "Allcargo", "Mahindra Logistics",
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
            f"due to heavy monsoon rainfall on the national highway. "
            f"Cargo value: ${value:,.2f}. "
            "The truck is stranded at a waterlogged checkpoint. "
            "Expected delay: 2-4 days. Customer is requesting urgent updates."
        ),
        carrier=carrier,
        value=value,
    )

    return Scenario(
        shipments=[shipment],
        total_budget=5_000.0,
        max_steps=5,
        description=(
            "A single shipment has been delayed due to monsoon flooding "
            "on the national highway. Investigate and resolve."
        ),
    )


def generate_medium_scenario(seed: int | None = None) -> Scenario:
    """Multiple exceptions requiring triage and prioritization."""
    rng = random.Random(seed)
    exception_configs: list[tuple[ExceptionType, Priority, int, str]] = [
        ("customs_hold", "critical", 3, "held at interstate customs checkpoint due to e-way bill mismatch"),
        ("damage_reported", "high", 5, "cargo damage reported during last-mile delivery in congested area"),
        ("weather_delay", "medium", 6, "delayed due to cyclone warning along eastern coast"),
        ("misroute", "high", 4, "incorrectly routed to wrong fulfilment centre during Diwali surge"),
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
            "Multiple shipments across Indian logistics corridors face different "
            "exceptions during festive season surge. Prioritize by SLA urgency "
            "and resolve each within budget."
        ),
    )


def generate_hard_scenario(seed: int | None = None) -> Scenario:
    """Cascading supply chain disruption with tight budget."""
    rng = random.Random(seed)

    # Major hub disruption affects multiple shipments
    closed_hub = rng.choice(["JNPT Mumbai", "Chennai Port", "Mundra Port"])

    exception_configs: list[tuple[ExceptionType, Priority, int, str]] = [
        ("port_closure", "critical", 2, f"stuck at {closed_hub} — cyclone alert closure"),
        ("port_closure", "critical", 3, f"rerouting needed due to {closed_hub} shutdown"),
        ("capacity_overflow", "high", 4, "warehouse overflow from diverted cargo in festive rush"),
        ("customs_hold", "high", 4, "GST compliance review triggered at state border"),
        ("damage_reported", "medium", 6, "cargo shifted during emergency reroute on NH-48"),
        ("carrier_breakdown", "medium", 5, "delivery truck breakdown on tier-2 city route"),
        ("documentation_error", "low", 7, "e-way bill mismatch from rush reroute"),
        ("misroute", "low", 8, "sent to wrong distribution hub during disruption"),
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
            f"Major disruption at {closed_hub} due to cyclone alert has caused "
            "cascading failures across 8 shipments on Indian logistics corridors. "
            "Budget is limited — you must triage and minimize total loss. "
            "Not all shipments can be fully resolved."
        ),
    )


SCENARIO_GENERATORS = {
    "easy": generate_easy_scenario,
    "medium": generate_medium_scenario,
    "hard": generate_hard_scenario,
}
