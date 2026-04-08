"""Quick inference test - just runs task_easy once."""

import os
import sys
from openenv.core.generic_client import GenericEnvClient

# Check token
HF_TOKEN = os.getenv("HF_TOKEN")
if not HF_TOKEN:
    print("ERROR: HF_TOKEN not set!")
    print("Run: set HF_TOKEN=hf_your_token")
    sys.exit(1)

ENV_URL = os.getenv("ENV_URL", "http://localhost:8000")

print(f"Testing connection to {ENV_URL}...")
print(f"Using token: {HF_TOKEN[:10]}...")

try:
    # Connect to environment
    client = GenericEnvClient(ENV_URL)

    print("\n✅ Connected to environment!")
    print("\nResetting task_easy...")

    # Reset
    obs = client.reset(task_id="task_easy")
    print(f"✅ Reset successful!")
    print(f"   Budget: ${obs.get('budget_remaining', 0)}")
    print(f"   Steps: {obs.get('time_remaining', 0)}")

    # Take one action
    print("\nExecuting investigate action...")
    obs = client.step({
        "action_type": "investigate",
        "target_shipment_id": "SHP-001",
        "parameters": {}
    })

    print(f"✅ Action successful!")
    print(f"   Reward: {obs.get('reward', 0):.4f}")
    print(f"   Budget: ${obs.get('budget_remaining', 0)}")
    print(f"   Feedback: {obs.get('feedback', '')[:100]}...")

    print("\n🎉 SUCCESS! Environment is working correctly!")
    print("\nNow run the full test:")
    print("  python inference.py")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("\nTroubleshooting:")
    print("1. Make sure server is running (start_server.cmd)")
    print("2. Check HF_TOKEN is valid")
    print("3. Verify ENV_URL is correct")
    sys.exit(1)
