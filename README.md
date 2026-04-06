---
title: MOGUL Logistics Environment Server
emoji: 📦
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
app_port: 8000
base_path: /web
tags:
  - openenv
---

# MOGUL Logistics - Shipment Exception Resolution Environment

An [OpenEnv](https://github.com/openenv-ai/openenv) environment where an AI agent learns to triage and resolve logistics shipment exceptions (delays, damages, misroutes, customs holds).

Built for the **OpenEnv AI ** by Meta, Hugging Face, PyTorch & Scaler School of Technology.

## Why This Environment

Shipment exceptions are the #1 operational pain point in logistics. Every carrier handles thousands daily. An LLM agent that learns to triage and resolve exceptions efficiently has genuine production value for RL training.

## Action Space

The agent can take the following actions on any active shipment:

| Action | Cost | Description |
|--------|------|-------------|
| `investigate` | $50 | Gather details about the exception (required before resolution actions) |
| `contact_carrier` | $100 | Reach out to the carrier for updates |
| `escalate` | $200 | Escalate to management for expedited review |
| `file_claim` | $300 | File an insurance or damage claim |
| `reschedule` | $800 | Reschedule delivery to a new date |
| `approve_refund` | $1,500 | Approve a customer refund |
| `reroute` | $2,000 | Reroute the shipment via alternative path |
| `split_shipment` | $2,500 | Split cargo across multiple shipments |

**Resolution constraint:** Only `reroute`, `reschedule`, `file_claim`, `approve_refund`, and `split_shipment` can mark a shipment as **resolved**. The other actions (`investigate`, `contact_carrier`, `escalate`) build progress but never trigger resolution.

**Investigation requirement:** Resolution actions require the shipment to be investigated first. Always `investigate` before attempting to resolve.

**Action format:**
```json
{
  "action_type": "investigate",
  "target_shipment_id": "SHP-001",
  "parameters": {}
}
```

## Observation Space

After each action, the agent receives:

| Field | Type | Description |
|-------|------|-------------|
| `shipment_status` | string | Summary table of all shipment statuses |
| `exception_details` | string | Text description of active exceptions |
| `available_actions` | list[str] | Valid action types |
| `budget_remaining` | float | Resolution budget left |
| `time_remaining` | int | Steps remaining |
| `resolution_progress` | dict | Per-shipment progress (0.0-1.0) |
| `feedback` | string | Result of last action |
| `done` | bool | Whether episode is complete |
| `reward` | float | Reward signal |

## SLA Mechanics

Each step decrements the SLA countdown for **all** unresolved shipments by 1. If a shipment's SLA reaches 0 before resolution, it permanently **fails**. This means the agent must triage — on harder tasks, not every shipment can be saved.

## Tasks

### Task 1: Single Delayed Shipment (Easy)
- **ID**: `task_easy`
- 1 shipment with a weather delay
- Max 5 steps, $5,000 budget
- Investigate → reroute or wait → confirm

### Task 2: Multi-Exception Triage (Medium)
- **ID**: `task_medium`
- 4 shipments with different exception types
- Max 10 steps, $12,000 budget
- Prioritize by SLA urgency, resolve each

### Task 3: Supply Chain Disruption (Hard)
- **ID**: `task_hard`
- 8 shipments with cascading port closure failures
- Max 15 steps, $15,000 budget
- Must triage — not all can be resolved

## Grading

Scores are in the range [0.0, 1.0] with four weighted components:

| Component | Weight | Description |
|-----------|--------|-------------|
| Resolution rate | 40% | Fraction of exceptions resolved |
| Cost efficiency | 25% | Budget remaining after resolution |
| SLA compliance | 20% | Fraction of shipments within SLA |
| Decision quality | 15% | Investigating before acting, priority ordering |

## Architecture

```
                    ┌─────────────────────────────────┐
                    │         inference.py             │
                    │   LLM Agent + Heuristic Fallback │
                    └──────────┬──────────────────────┘
                               │ HTTP (reset/step)
                    ┌──────────▼──────────────────────┐
                    │       FastAPI (server/app.py)    │
                    │   /reset  /step  /state  /health │
                    │   /api/schema  /api/mcp/tools    │
                    └──────────┬──────────────────────┘
                               │
          ┌────────────────────▼────────────────────┐
          │     ShipmentEnvironment (environment.py) │
          │   reset() → Observation                  │
          │   step(Action) → Observation + Reward    │
          └──────┬──────────────────┬───────────────┘
                 │                  │
    ┌────────────▼───────┐  ┌──────▼──────────────┐
    │  scenarios.py      │  │  graders.py         │
    │  Easy/Medium/Hard  │  │  grade_episode()    │
    │  scenario gen      │  │  4-component score  │
    └────────────────────┘  └─────────────────────┘
```

## Strategy Guide

The agent must resolve shipments before SLA deadlines while staying under budget:

| Path | Steps | Cost | When to Use |
|------|-------|------|-------------|
| **Fast** (3 steps) | investigate → approve_refund → reschedule | $2,350 | SLA is tight (< 4 steps) |
| **Cheap** (4 steps) | investigate → escalate → file_claim → reschedule | $1,350 | SLA allows (>= 4 steps) |

**Tips:**
- Always investigate before resolution actions
- Work on the shipment with the tightest SLA first
- Use the cheap path when SLA allows — saves $1,000 per shipment
- After resolving salvageable ships, investigate remaining for decision quality points
- Higher-priority shipments first for better DQ score

## Evaluation

Scores are computed as a weighted composite in [0.0, 1.0]:

| Component | Weight | Formula |
|-----------|--------|---------|
| Resolution rate | 40% | `resolved / total` |
| Cost efficiency | 25% | `1 - (cost_spent / budget)` |
| SLA compliance | 20% | `1 - (violations / total)` |
| Decision quality | 15% | `0.6 * investigate_first + 0.4 * priority_order` |

## Connecting as an External Agent

Any HTTP client can interact with the environment:

```python
import requests

BASE = "https://muhammedsayeedurrahman-mogul-logistics.hf.space"

# 1. Reset to start an episode
obs = requests.post(f"{BASE}/reset", json={"task_id": "task_easy"}).json()

# 2. Take actions until done
while not obs["done"]:
    action = {
        "action": {
            "action_type": "investigate",
            "target_shipment_id": "SHP-001",
            "parameters": {}
        }
    }
    obs = requests.post(f"{BASE}/step", json=action).json()
    print(f"Reward: {obs['reward']}, Done: {obs['done']}")
```

Full API schema available at: `/docs` (Swagger) or `/schema` (JSON).

## Setup

```bash
# Install dependencies
pip install -e ".[inference]"

# Start the server
uvicorn server.app:app --port 8000

# Run the inference agent
python inference.py
```

## Testing

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_graders.py -v
pytest tests/test_environment.py -v
```

Tests cover: grading math, environment step/reset/validation, SLA mechanics, scenario generation, Pydantic model validation, and heuristic planner behavior.

## Docker

```bash
docker build -t mogul-logistics .
docker run -p 8000:8000 mogul-logistics
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/reset` | Reset environment (body: `{"task_id": "task_easy"}`) |
| POST | `/step` | Execute action |
| GET | `/state` | Get current episode state |
| GET | `/health` | Health check |
| GET | `/schema` | JSON schemas for action/observation |
| GET | `/metadata` | Environment metadata |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HF_TOKEN` | — | HuggingFace API token (for inference.py) |
| `API_BASE_URL` | `https://router.huggingface.co/v1` | LLM API base URL |
| `MODEL_NAME` | `meta-llama/Llama-3.3-70B-Instruct` | Model for the agent |
| `ENV_URL` | `http://localhost:8000` | Environment server URL |
| `ENABLE_WEB_INTERFACE` | `false` | Enable Gradio web UI at /web |
