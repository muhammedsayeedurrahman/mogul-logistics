"""Local inference test - uses heuristic agent, no HF_TOKEN required.

This tests the complete inference loop locally using the heuristic planner
instead of LLM, so it can run without API credentials.
"""

import asyncio
import sys
from pathlib import Path

# Add server to path
sys.path.insert(0, str(Path(__file__).parent))

from openenv.core.generic_client import GenericEnvClient
from server.heuristic import HeuristicPlanner
from server.constants import ACTION_COSTS


async def test_local_inference():
    """Run complete inference loop using heuristic agent."""

    print("=" * 60)
    print("LOCAL INFERENCE TEST (No HF_TOKEN Required)")
    print("=" * 60)

    # Configuration
    ENV_URL = "http://localhost:8000"
    TASKS = ["task_easy", "task_medium", "task_hard"]

    print(f"\n✓ Environment URL: {ENV_URL}")
    print(f"✓ Testing {len(TASKS)} difficulty tiers")
    print(f"✓ Using HeuristicPlanner (no LLM required)\n")

    # Connect to environment
    try:
        client = GenericEnvClient(ENV_URL)
        print("✓ Connected to environment successfully\n")
    except Exception as e:
        print(f"✗ ERROR: Could not connect to {ENV_URL}")
        print(f"  Make sure server is running: start_server.cmd")
        print(f"  Error: {e}")
        return False

    # Test each difficulty tier
    results = []

    for task_id in TASKS:
        print(f"\n{'=' * 60}")
        print(f"TESTING: {task_id.upper()}")
        print(f"{'=' * 60}\n")

        # Initialize planner
        planner = HeuristicPlanner()

        # Reset environment
        try:
            obs = client.reset(task_id=task_id)
            print(f"✓ Reset successful")
            print(f"  Budget: ${obs.get('budget_remaining', 0):,}")
            print(f"  Steps: {obs.get('time_remaining', 0)}")

            # Count shipments
            shipment_status = obs.get('shipment_status', '')
            num_shipments = len([line for line in shipment_status.split('\n') if 'SHP-' in line])
            print(f"  Shipments: {num_shipments}\n")
        except Exception as e:
            print(f"✗ ERROR during reset: {e}")
            return False

        # Run episode
        step_count = 0
        total_cost = 0
        done = False
        actions_taken = []

        while not done:
            # Get action from heuristic planner
            action, explanation = planner.pick_action(obs)

            step_count += 1
            cost = ACTION_COSTS.get(action["action_type"], 0)
            total_cost += cost

            print(f"[Step {step_count}] {action['action_type']}({action['target_shipment_id']}) ${cost:,}")
            print(f"  → {explanation}")

            actions_taken.append(action["action_type"])

            # Execute action
            try:
                result = client.step(action)
                obs = result.get("observation", {})
                reward = result.get("reward", 0.0)
                done = result.get("done", False)

                if done:
                    print(f"\n✓ Episode completed!")
                    print(f"  Final reward: {reward:.4f}")
                    print(f"  Steps taken: {step_count}")
                    print(f"  Total cost: ${total_cost:,}")

                    results.append({
                        "task": task_id,
                        "reward": reward,
                        "steps": step_count,
                        "cost": total_cost,
                        "success": reward >= 0.5,
                    })

            except Exception as e:
                print(f"✗ ERROR during step: {e}")
                return False

            # Safety limit
            if step_count > 50:
                print(f"\n✗ ERROR: Exceeded 50 steps (infinite loop?)")
                return False

    # Print summary
    print(f"\n\n{'=' * 60}")
    print("INFERENCE TEST SUMMARY")
    print(f"{'=' * 60}\n")

    for result in results:
        status = "✓ PASS" if result["success"] else "✗ FAIL"
        print(f"{result['task']:15} {status}  reward={result['reward']:.4f}  steps={result['steps']:2}  cost=${result['cost']:,}")

    # Overall pass/fail
    all_passed = all(r["success"] for r in results)

    print(f"\n{'=' * 60}")
    if all_passed:
        print("✓ ALL TESTS PASSED - Inference system working correctly!")
    else:
        print("✗ SOME TESTS FAILED - Check results above")
    print(f"{'=' * 60}\n")

    return all_passed


def main():
    """Run the test."""
    print("\n🧪 Starting local inference test...\n")

    # Check if server is accessible
    import requests
    try:
        resp = requests.get("http://localhost:8000/health", timeout=5)
        if resp.status_code != 200:
            print("✗ ERROR: Server returned non-200 status")
            print("  Make sure server is running: start_server.cmd")
            sys.exit(1)
    except Exception as e:
        print("✗ ERROR: Cannot connect to server at http://localhost:8000")
        print("  Make sure server is running: start_server.cmd")
        print(f"  Error: {e}")
        sys.exit(1)

    # Run async test
    success = asyncio.run(test_local_inference())

    if success:
        print("\n🎉 SUCCESS! Inference system is working correctly!")
        print("\nNext steps:")
        print("1. Set HF_TOKEN environment variable")
        print("2. Run full LLM inference: python inference.py")
        print("3. Compare LLM performance vs heuristic baseline\n")
        sys.exit(0)
    else:
        print("\n❌ FAILURE! Check errors above")
        sys.exit(1)


if __name__ == "__main__":
    main()
