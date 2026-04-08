"""Ultra-simple test to verify environment works."""

import requests
import json

print("=" * 60)
print("SIMPLE ENVIRONMENT TEST")
print("=" * 60)

BASE_URL = "http://localhost:8000"

# 1. Health check
print("\n1. Testing health endpoint...")
try:
    resp = requests.get(f"{BASE_URL}/health")
    print(f"   ✓ Health: {resp.json()}")
except Exception as e:
    print(f"   ✗ Error: {e}")
    exit(1)

# 2. Reset
print("\n2. Testing reset...")
try:
    resp = requests.post(f"{BASE_URL}/reset", json={"task_id": "task_easy"})
    data = resp.json()
    print(f"   ✓ Reset successful")
    print(f"   Budget: ${data['observation']['budget_remaining']}")
    print(f"   Steps: {data['observation']['time_remaining']}")
except Exception as e:
    print(f"   ✗ Error: {e}")
    exit(1)

# 3. Step
print("\n3. Testing step (investigate SHP-001)...")
try:
    resp = requests.post(f"{BASE_URL}/step", json={
        "action_type": "investigate",
        "target_shipment_id": "SHP-001",
        "parameters": {}
    })
    data = resp.json()
    print(f"   ✓ Step successful")
    print(f"   Reward: {data['reward']:.4f}")
    print(f"   Budget: ${data['observation']['budget_remaining']}")
except Exception as e:
    print(f"   ✗ Error: {e}")
    exit(1)

print("\n" + "=" * 60)
print("✓ ALL TESTS PASSED - Environment is working!")
print("=" * 60)
print("\nThe API works fine. The issue is with the web interface display.")
print("Please share a screenshot of what you see at http://localhost:8000")
