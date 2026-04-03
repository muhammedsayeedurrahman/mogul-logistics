"""Local client for testing the environment."""

from __future__ import annotations

import asyncio

from openenv.core.generic_client import GenericEnvClient


async def main() -> None:
    """Run a quick smoke test against the local server."""
    async with GenericEnvClient(base_url="http://localhost:8000") as env:
        # Reset with easy task
        result = await env.reset(task_id="task_easy")
        print("=== RESET (task_easy) ===")
        print(f"Observation: {result.observation}")
        print(f"Done: {result.done}")
        print()

        # Investigate the shipment
        result = await env.step(
            {
                "action_type": "investigate",
                "target_shipment_id": "SHP-001",
                "parameters": {},
            }
        )
        print("=== STEP 1: investigate ===")
        print(f"Feedback: {result.observation.get('feedback', '')}")
        print(f"Reward: {result.reward}")
        print()

        # Reroute
        result = await env.step(
            {
                "action_type": "reroute",
                "target_shipment_id": "SHP-001",
                "parameters": {"new_route": "via_air"},
            }
        )
        print("=== STEP 2: reroute ===")
        print(f"Feedback: {result.observation.get('feedback', '')}")
        print(f"Reward: {result.reward}")
        print(f"Done: {result.done}")
        print()

        # Get state
        state = await env.state()
        print("=== STATE ===")
        print(state)


if __name__ == "__main__":
    asyncio.run(main())
