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

# MOGUL Logistics — Real-World Indian Supply-Chain Optimization Using RL

An [OpenEnv](https://github.com/openenv-ai/openenv) reinforcement learning environment where AI agents learn to triage and resolve logistics shipment exceptions — delays, damages, misroutes, customs holds — across India's complex supply-chain network.

Built for the **OpenEnv AI Hackathon** by Meta, Hugging Face, PyTorch & Scaler School of Technology.

## Why This Matters

India's logistics sector handles **$400B+ in annual freight** across a fragmented network of roads, rail, ports, and last-mile delivery. Shipment exceptions — weather disruptions during monsoon, e-way bill mismatches at state borders, festival surge overloads during Diwali — cost the industry billions annually.

MOGUL Logistics provides a realistic RL training ground where agents learn to:
- **Triage** exceptions by SLA urgency across 10 Indian logistics hubs
- **Optimize** resolution cost (choosing between ₹1,350 cheap paths vs ₹2,350 fast paths)
- **Handle uncertainty** — cascading port closures, customs holds, multi-modal transport failures
- **Scale** from single-shipment incidents to 8-shipment supply-chain disruptions

## Key Features

| Feature | Description |
|---------|-------------|
| **3 difficulty tiers** | Easy (1 shipment) → Medium (4 shipments) → Hard (8 with cascading failures) |
| **Composite reward** | 4-component weighted scoring: resolution, cost efficiency, SLA, decision quality |
| **Indian logistics network** | Real routes between Mumbai, Delhi NCR, Chennai, Bangalore, Kolkata, and more |
| **Indian carriers** | Blue Dart, Delhivery, Gati, Rivigo, SafeXpress, TCI Express, etc. |
| **India-specific scenarios** | Monsoon disruptions, GST/e-way bill compliance, festival surges, port closures |
| **Interactive dashboard** | Real-time route maps, agent activity feed, training performance charts |
| **MCP integration** | `/api/mcp/tools` endpoint for AI agent discovery |
| **PyTorch training demo** | REINFORCE policy that achieves 234% improvement over random baseline |

## Agent Performance (Before vs After)

| Agent | Avg Reward | Improvement |
|-------|-----------|-------------|
| Random (baseline) | 0.2344 | — |
| **Trained Policy** (100 episodes REINFORCE) | 0.7825 | **+234%** over random |
| Heuristic (expert rules) | 0.8975 | +283% over random |

The trained neural network policy learns meaningful logistics decision-making in just 100 episodes, demonstrating a clear learnable reward signal — the core requirement for a useful RL environment.

## Action Space

8 actions with increasing cost and impact:

| Action | Cost | Description |
|--------|------|-------------|
| `investigate` | $50 | Gather details about the exception (required first) |
| `contact_carrier` | $100 | Reach out to the carrier for updates |
| `escalate` | $200 | Escalate to management for expedited review |
| `file_claim` | $300 | File an insurance or damage claim |
| `reschedule` | $800 | Reschedule delivery to a new date |
| `approve_refund` | $1,500 | Approve a customer refund |
| `reroute` | $2,000 | Reroute shipment via alternative path |
| `split_shipment` | $2,500 | Split cargo across multiple shipments |

**Resolution constraint:** Only `reroute`, `reschedule`, `file_claim`, `approve_refund`, and `split_shipment` can resolve a shipment. Other actions build progress but never trigger resolution.

**Investigation requirement:** Resolution actions require the shipment to be investigated first. Always `investigate` before attempting to resolve.

## Observation Space

After each action, the agent receives:

| Field | Type | Description |
|-------|------|-------------|
| `shipment_status` | string | Summary table of all shipment statuses |
| `exception_details` | string | Text description of active exceptions |
| `available_actions` | list[str] | Valid action types |
| `budget_remaining` | float | Resolution budget left |
| `time_remaining` | int | Steps remaining |
| `resolution_progress` | dict | Per-shipment progress (0.0–1.0) |
| `feedback` | string | Result of last action |
| `done` | bool | Whether episode is complete |
| `reward` | float | Reward signal |

## SLA Mechanics

Each step decrements the SLA countdown for **all** unresolved shipments by 1. If a shipment's SLA reaches 0 before resolution, it permanently **fails**. The agent must triage — on harder tasks, not every shipment can be saved.

## Tasks

### Task 1: Single Delayed Shipment (`task_easy`)
- 1 shipment with a weather delay (e.g., heavy monsoon on NH48)
- Max 5 steps, $5,000 budget
- Tests basic investigate → resolve flow

### Task 2: Multi-Exception Triage (`task_medium`)
- 4 shipments with different exceptions — e-way bill mismatch, Diwali surge, cyclone warning
- Max 10 steps, $12,000 budget
- Requires SLA-based prioritization

### Task 3: Supply Chain Disruption (`task_hard`)
- 8 shipments with cascading failures from port closure (JNPT Mumbai / Chennai Port / Mundra Port)
- Max 15 steps, $15,000 budget
- Must triage — not all shipments can be saved

## Reward Function

Scores are in [0.0, 1.0] with four weighted components:

| Component | Weight | Formula |
|-----------|--------|---------|
| Resolution rate | 40% | `resolved / total` |
| Cost efficiency | 25% | `1 - (cost_spent / budget)` |
| SLA compliance | 20% | `1 - (violations / total)` |
| Decision quality | 15% | `0.6 × investigate_first + 0.4 × priority_order` |

This composite reward encourages realistic logistics behavior: resolve exceptions efficiently, minimize cost, meet deadlines, and follow proper investigation protocols.

## Sample Training Code (PyTorch)

```python
import torch
import torch.nn as nn
from server.environment import ShipmentEnvironment
from train_demo import extract_features, decode_action

# Build a small MLP policy
policy = nn.Sequential(
    nn.Linear(26, 64), nn.ReLU(),
    nn.Linear(64, 32), nn.ReLU(),
    nn.Linear(32, 64),  # 8 actions × 8 shipment slots
)
optimizer = torch.optim.Adam(policy.parameters(), lr=1e-3)

env = ShipmentEnvironment()

for episode in range(100):
    obs = env.reset(seed=episode, task_id="task_easy")
    log_probs, rewards = [], []

    while not obs.done:
        features = torch.tensor(extract_features(obs), dtype=torch.float32).unsqueeze(0)
        logits = policy(features)
        dist = torch.distributions.Categorical(torch.softmax(logits, dim=-1))
        action_idx = dist.sample()
        log_probs.append(dist.log_prob(action_idx))

        action = decode_action(action_idx.item(), obs)
        if action is None:
            break  # invalid action — fallback or end
        obs = env.step(action)
        rewards.append(obs.reward or 0.0)

    # REINFORCE update
    G, returns = 0.0, []
    for r in reversed(rewards):
        G = r + 0.99 * G
        returns.insert(0, G)
    returns = torch.tensor(returns)
    if returns.std() > 1e-6:
        returns = (returns - returns.mean()) / (returns.std() + 1e-8)

    loss = sum(-lp * R for lp, R in zip(log_probs, returns))
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
```

Run the full training demo:
```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
python train_demo.py
# Outputs: assets/training_curve.json, assets/trained_policy.pt
```

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
    │  India-specific    │  │  grade_episode()    │
    │  scenario gen      │  │  4-component score  │
    └────────────────────┘  └─────────────────────┘
```

## Dashboard

The interactive Gradio dashboard includes:
- **Route map** — Plotly geospatial visualization of Indian logistics network with live shipment tracking
- **Agent activity feed** — Real-time step-by-step display of agent decisions
- **Training comparison** — Side-by-side Random vs Heuristic vs Trained Policy performance
- **Shipment status table** — Color-coded per-shipment progress and SLA countdown

Enable the dashboard:
```bash
ENABLE_WEB_INTERFACE=true uvicorn server.app:app --port 8000
# Dashboard available at http://localhost:8000/web
```

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

Full API schema: `/docs` (Swagger) or `/schema` (JSON).

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

# Run all 69 tests
pytest tests/ -v
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
| POST | `/reset` | Reset environment (`{"task_id": "task_easy"}`) |
| POST | `/step` | Execute action |
| GET | `/state` | Get current episode state |
| GET | `/health` | Health check |
| GET | `/schema` | JSON schemas for action/observation |
| GET | `/metadata` | Environment metadata |
| GET | `/api/mcp/tools` | MCP tool discovery for AI agents |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HF_TOKEN` | — | HuggingFace API token (for inference.py) |
| `API_BASE_URL` | `https://router.huggingface.co/v1` | LLM API base URL |
| `MODEL_NAME` | `meta-llama/Llama-3.3-70B-Instruct` | Model for the agent |
| `ENV_URL` | `http://localhost:8000` | Environment server URL |
| `ENABLE_WEB_INTERFACE` | `false` | Enable Gradio web UI at /web |

## Innovation Highlights

- **Multi-agent cooperation potential** — The environment supports multiple concurrent shipment resolution, enabling multi-agent RL research (e.g., separate agents for triage vs resolution)
- **Uncertainty handling** — Stochastic scenario generation with varying SLA pressures and cascading failures mirrors real-world logistics unpredictability
- **Scalability** — From single-shipment training wheels to 8-shipment supply-chain crises, the difficulty tiers enable curriculum learning
- **Real-world grounding** — Indian logistics network with actual carrier names, city routes, and domain-specific exceptions (GST compliance, monsoon disruptions, port closures)
- **Cost-aware decision making** — Budget constraints force the agent to learn economically optimal resolution strategies, not just fast ones

## License

MIT
