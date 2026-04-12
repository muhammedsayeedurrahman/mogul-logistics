---
title: MOGUL Logistics
emoji: "\U0001F69B"
colorFrom: red
colorTo: yellow
sdk: docker
app_port: 8000
pinned: false
short_description: RL environment for India's freight network (Meta OpenEnv)
---

# MOGUL Logistics

> OpenEnv RL environment for training AI agents to resolve logistics exceptions across India's freight network.

**Live:** https://muhammedsayeedurrahman-mogul-logistics.hf.space | **Source:** https://github.com/muhammedsayeedurrahman/mogul-logistics

---

## Quick Start

```bash
# Clone and install
git clone https://github.com/muhammedsayeedurrahman/mogul-logistics
cd mogul-logistics
pip install -e ".[inference,dev]"

# Start server
uvicorn server.app:app --host 0.0.0.0 --port 8000

# Run inference agent (in another terminal)
export HF_TOKEN="hf_your_token"
python inference.py
```

Or visit the [live demo](https://muhammedsayeedurrahman-mogul-logistics.hf.space) and click **Run Agent Demo**.

---

## What It Does

An AI agent manages shipment exceptions (monsoon delays, customs holds, port closures, cargo damage) across India's freight corridors. Each step, SLA clocks tick down on all active shipments. The agent must triage, investigate, and resolve exceptions before deadlines expire — under budget.

**8 actions** with cost/progress trade-offs:

| Action | Cost | Progress | Needs Investigation |
|--------|------|----------|:-------------------:|
| `investigate` | $50 | +15% | No |
| `contact_carrier` | $100 | +10% | No |
| `escalate` | $200 | +20% | No |
| `file_claim` | $300 | +30% | Yes |
| `reschedule` | $800 | +35% | Yes |
| `approve_refund` | $1,500 | +50% | Yes |
| `reroute` | $2,000 | +40% | Yes |
| `split_shipment` | $2,500 | +45% | Yes |

**Optimal paths:**
- Fast (3 steps, $2,350): `investigate` -> `approve_refund` -> `reschedule`
- Cheap (4 steps, $1,350): `investigate` -> `escalate` -> `file_claim` -> `reschedule`

---

## 3 Task Tiers

| Tier | Shipments | Budget | Steps | Challenge |
|------|-----------|--------|-------|-----------|
| **Easy** | 1 | $5,000 | 5 | Single delayed shipment |
| **Medium** | 4 | $12,000 | 10 | Multi-exception triage (customs, damage, weather, misroute) |
| **Hard** | 8 | $15,000 | 15 | Cascading port closure — not all shipments can be saved |

---

## Grading (Composite Reward 0.0 - 1.0)

```
Score = 0.40 x resolution_rate       # shipments resolved / total
      + 0.25 x cost_efficiency       # 1 - (spent / budget)
      + 0.20 x sla_compliance        # 1 - (violations / total)
      + 0.15 x decision_quality      # investigate-first + priority ordering
```

Grading implementation: [`server/graders.py`](server/graders.py)

---

## Training Results

PyTorch REINFORCE policy trained on each difficulty tier. All scores use the same 0.0-1.0 composite grade.

| Agent | Easy | Medium | Hard |
|-------|:----:|:------:|:----:|
| Random baseline | 0.262 | 0.222 | 0.208 |
| **Trained (REINFORCE)** | **0.853** | **0.578** | **0.372** |
| Heuristic expert | 0.898 | 0.592 | 0.430 |

- Easy: **+226%** over random, reaches **95%** of expert in 80 episodes
- Medium: **+160%** over random, reaches **98%** of expert in 200 episodes
- Hard: **+79%** over random, reaches **87%** of expert in 200 episodes

Reproducible: `python train_demo.py`. Raw data: [`assets/training_curve.json`](assets/training_curve.json).

---

## Inference Output

```
[START] task=task_easy env=mogul-logistics model=meta-llama/Llama-3.3-70B-Instruct
  [HEURISTIC] investigate(SHP-001) — Investigating SHP-001 first
[STEP] step=1 action=investigate(SHP-001) reward=0.05 done=False error=None
  [HEURISTIC] approve_refund(SHP-001) — Approve refund for SHP-001
[STEP] step=2 action=approve_refund(SHP-001) reward=0.065 done=False error=None
  [HEURISTIC] reschedule(SHP-001) — reschedule will finish SHP-001
[STEP] step=3 action=reschedule(SHP-001) reward=0.8975 done=True error=None
[END] success=True steps=3 score=0.8975 rewards=[0.05, 0.065, 0.8975]
```

---

## OpenEnv Compliance

- `openenv.yaml` — spec v1, 3 tasks defined
- `POST /reset` — initialize episode, returns observation
- `POST /step` — execute action, returns (observation, reward, done)
- `GET /state` — episode metadata
- `inference.py` — `[START]`/`[STEP]`/`[END]` structured logging
- `HF_TOKEN`, `API_BASE_URL`, `MODEL_NAME` env vars supported
- Dockerfile builds and deploys to HF Spaces
- Runtime < 20 min on 2 vCPU / 8 GB RAM

---

## Project Structure

```
server/
  environment.py    # Core RL env (reset/step/state)
  scenarios.py      # India-specific scenario generators
  graders.py        # 4-component reward function
  heuristic.py      # Expert baseline planner
  tasks.py          # 3 difficulty tiers
  constants.py      # Action costs and progress values
  app.py            # FastAPI + Gradio entry point
  gradio_custom.py  # Live demo dashboard
models.py           # Pydantic schemas (Action/Observation/State)
inference.py        # LLM agent with heuristic fallback
train_demo.py       # PyTorch REINFORCE training
tests/              # Test suite
openenv.yaml        # Environment manifest
Dockerfile          # HF Spaces deployment
```

---

## Docker

```bash
docker build -t mogul-logistics .
docker run -p 8000:8000 -e HF_TOKEN="your_token" mogul-logistics
```

---

**Author:** Muhammed Sayeedur Rahman | **Hackathon:** Meta PyTorch OpenEnv 2026 | **License:** MIT
