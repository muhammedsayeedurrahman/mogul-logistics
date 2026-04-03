"""
Comprehensive test script for MOGUL Logistics Environment.

Usage:
    # With server running locally:
    python test_all.py

    # Against a remote server:
    python test_all.py --url http://some-server:8000
"""

from __future__ import annotations

import asyncio
import sys

from openenv.core.generic_client import GenericEnvClient

ENV_URL = "http://localhost:8000"
if len(sys.argv) > 2 and sys.argv[1] == "--url":
    ENV_URL = sys.argv[2]

DIVIDER = "=" * 60


def print_obs(obs: dict, step_label: str) -> None:
    print(f"\n--- {step_label} ---")
    print(f"  Feedback : {obs.get('feedback', '')}")
    print(f"  Budget   : ${obs.get('budget_remaining', 0):,.0f}")
    print(f"  Steps    : {obs.get('time_remaining', 0)} remaining")
    progress = obs.get("resolution_progress", {})
    if progress:
        for sid, pct in progress.items():
            bar = "#" * int(pct * 20) + "-" * (20 - int(pct * 20))
            print(f"  {sid}  [{bar}] {pct:.0%}")


# ------------------------------------------------------------------
# Test 1: Easy Task — Single Delayed Shipment
# ------------------------------------------------------------------
async def test_easy() -> float:
    print(f"\n{DIVIDER}")
    print("TEST 1: EASY — Single Delayed Shipment")
    print(f"{DIVIDER}")

    async with GenericEnvClient(base_url=ENV_URL) as env:
        result = await env.reset(task_id="task_easy")
        print_obs(result.observation, "RESET")

        # Step 1: Investigate
        result = await env.step({
            "action_type": "investigate",
            "target_shipment_id": "SHP-001",
            "parameters": {},
        })
        print_obs(result.observation, "STEP 1: investigate SHP-001")

        # Step 2: Contact carrier
        result = await env.step({
            "action_type": "contact_carrier",
            "target_shipment_id": "SHP-001",
            "parameters": {},
        })
        print_obs(result.observation, "STEP 2: contact_carrier SHP-001")

        # Step 3: Reroute
        result = await env.step({
            "action_type": "reroute",
            "target_shipment_id": "SHP-001",
            "parameters": {"new_route": "via_air"},
        })
        print_obs(result.observation, "STEP 3: reroute SHP-001")

        score = result.reward if result.reward is not None else 0.0
        done = result.done
        print(f"\n  Done: {done} | Score: {score:.4f}")
        return score


# ------------------------------------------------------------------
# Test 2: Medium Task — Multi-Exception Triage
# ------------------------------------------------------------------
async def test_medium() -> float:
    print(f"\n{DIVIDER}")
    print("TEST 2: MEDIUM — Multi-Exception Triage (4 shipments)")
    print(f"{DIVIDER}")

    actions = [
        ("investigate",     "SHP-001", {}),  # customs_hold (critical)
        ("escalate",        "SHP-001", {"reason": "customs deadline approaching"}),
        ("investigate",     "SHP-004", {}),  # misroute (high)
        ("reroute",         "SHP-004", {}),  # fix the misroute
        ("investigate",     "SHP-002", {}),  # damage_reported (high)
        ("file_claim",      "SHP-002", {}),  # file insurance claim
        ("investigate",     "SHP-003", {}),  # weather_delay (medium)
        ("contact_carrier", "SHP-003", {}),  # check on weather
        ("reschedule",      "SHP-003", {}),  # reschedule delivery
    ]

    async with GenericEnvClient(base_url=ENV_URL) as env:
        result = await env.reset(task_id="task_medium")
        print_obs(result.observation, "RESET")

        for i, (action_type, shipment_id, params) in enumerate(actions, 1):
            result = await env.step({
                "action_type": action_type,
                "target_shipment_id": shipment_id,
                "parameters": params,
            })
            print_obs(result.observation, f"STEP {i}: {action_type} {shipment_id}")

            if result.done:
                break

        score = result.reward if result.reward is not None else 0.0
        print(f"\n  Done: {result.done} | Score: {score:.4f}")
        return score


# ------------------------------------------------------------------
# Test 3: Hard Task — Supply Chain Disruption
# ------------------------------------------------------------------
async def test_hard() -> float:
    print(f"\n{DIVIDER}")
    print("TEST 3: HARD — Supply Chain Disruption (8 shipments)")
    print(f"{DIVIDER}")

    # Strategy: focus on critical/high priority, triage the rest
    actions = [
        ("investigate",     "SHP-001", {}),  # port_closure (critical)
        ("investigate",     "SHP-002", {}),  # port_closure (critical)
        ("reroute",         "SHP-001", {}),  # fix critical
        ("reroute",         "SHP-002", {}),  # fix critical
        ("investigate",     "SHP-003", {}),  # capacity_overflow (high)
        ("investigate",     "SHP-004", {}),  # customs_hold (high)
        ("escalate",        "SHP-004", {"reason": "customs urgency"}),
        ("reschedule",      "SHP-003", {}),  # handle overflow
        ("investigate",     "SHP-005", {}),  # damage (medium)
        ("file_claim",      "SHP-005", {}),  # file claim
        ("investigate",     "SHP-006", {}),  # carrier_breakdown (medium)
        ("contact_carrier", "SHP-006", {}),
    ]

    async with GenericEnvClient(base_url=ENV_URL) as env:
        result = await env.reset(task_id="task_hard")
        print_obs(result.observation, "RESET")

        for i, (action_type, shipment_id, params) in enumerate(actions, 1):
            result = await env.step({
                "action_type": action_type,
                "target_shipment_id": shipment_id,
                "parameters": params,
            })
            print_obs(result.observation, f"STEP {i}: {action_type} {shipment_id}")

            if result.done:
                break

        score = result.reward if result.reward is not None else 0.0
        print(f"\n  Done: {result.done} | Score: {score:.4f}")
        return score


# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------
async def main() -> None:
    print(DIVIDER)
    print("  MOGUL LOGISTICS — Shipment Exception Resolution")
    print("  Test Runner")
    print(f"  Server: {ENV_URL}")
    print(DIVIDER)

    scores: dict[str, float] = {}

    try:
        scores["task_easy"] = await test_easy()
    except Exception as e:
        print(f"\n  [ERROR] Easy task failed: {e}")
        scores["task_easy"] = 0.0

    try:
        scores["task_medium"] = await test_medium()
    except Exception as e:
        print(f"\n  [ERROR] Medium task failed: {e}")
        scores["task_medium"] = 0.0

    try:
        scores["task_hard"] = await test_hard()
    except Exception as e:
        print(f"\n  [ERROR] Hard task failed: {e}")
        scores["task_hard"] = 0.0

    # Final summary
    print(f"\n\n{DIVIDER}")
    print("  FINAL RESULTS")
    print(DIVIDER)
    for tid, sc in scores.items():
        emoji = "PASS" if sc > 0.3 else "FAIL"
        print(f"  [{emoji}] {tid:15s} — score: {sc:.4f}")

    avg = sum(scores.values()) / max(len(scores), 1)
    print(f"\n  AVERAGE SCORE: {avg:.4f}")
    print(DIVIDER)


if __name__ == "__main__":
    asyncio.run(main())
