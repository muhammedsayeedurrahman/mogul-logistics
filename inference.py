"""Evaluation script — drives the LLM agent through the environment.

Uses HuggingFace Router (no OpenAI key needed).
Must complete in <20 minutes on 2 vCPU / 8GB RAM.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
import time

from openenv.core.generic_client import GenericEnvClient

from server.constants import ACTION_COSTS, VALID_ACTIONS
from server.heuristic import HeuristicPlanner

# ---------------------------------------------------------------------------
# LLM client setup — HuggingFace router (uses required env vars)
# ---------------------------------------------------------------------------
try:
    from openai import OpenAI
except ImportError:
    print("[ERROR] openai package not installed. Run: pip install openai")
    sys.exit(1)

HF_TOKEN = os.environ.get("HF_TOKEN", "")
API_BASE_URL = os.environ.get(
    "API_BASE_URL", "https://router.huggingface.co/v1"
)
MODEL_NAME = os.environ.get(
    "MODEL_NAME", "meta-llama/Llama-3.3-70B-Instruct"
)

# LLM is optional: if HF_TOKEN is missing, fall back to the trained
# heuristic planner only. This lets local judges run inference.py with
# zero config. When HF_TOKEN is set, the LLM gets first try per step.
_LLM_ENABLED = bool(HF_TOKEN)
llm = OpenAI(
    base_url=API_BASE_URL,
    api_key=HF_TOKEN or "sk-noop",
) if _LLM_ENABLED else None

ENV_URL = os.environ.get("ENV_URL", "http://localhost:8000")
TASKS = ["task_easy", "task_medium", "task_hard"]

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# LLM agent — primary decision maker with heuristic fallback
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """\
You are a logistics exception resolution agent for MOGUL Logistics. \
Your goal: resolve as many shipment exceptions as possible before SLA \
deadlines expire, while staying under budget.

IMPORTANT RULES:
- Each step decrements ALL active shipments' SLA by 1.
- You must investigate a shipment before using resolution actions on it.
- Resolution actions: reroute ($2000), reschedule ($800), file_claim ($300), \
approve_refund ($1500), split_shipment ($2500).
- Non-resolution actions: investigate ($50), contact_carrier ($100), escalate ($200).

OPTIMAL STRATEGY:
1. Work on the shipment with the TIGHTEST SLA first (fewest steps remaining).
2. Skip doomed shipments (SLA < 3 and progress = 0%).
3. If already working on a shipment (progress > 0%), FINISH IT first.
4. Fast path (3 steps, $2,350): investigate -> approve_refund -> reschedule = 100%.
5. Cheap path (4 steps, $1,350): investigate -> escalate -> file_claim -> reschedule = 100%.
6. Use cheap path when SLA allows (>= 4 steps), fast path when SLA is tight.
7. After resolving all salvageable ships, investigate remaining by priority for DQ points.

Respond with ONLY a JSON object (no markdown, no extra text):
{"action_type": "<action>", "target_shipment_id": "<SHP-XXX>", "parameters": {}}
"""


def _is_valid_llm_action(action: dict, observation: dict) -> bool:
    """Check if an LLM-produced action is valid and affordable."""
    atype = action.get("action_type", "")
    target = action.get("target_shipment_id", "")
    if atype not in VALID_ACTIONS:
        return False
    if not target:
        return False
    cost = ACTION_COSTS.get(atype, float("inf"))
    budget = observation.get("budget_remaining", 0)
    if cost > budget:
        return False
    return True


def ask_llm(
    messages: list[dict],
    observation: dict,
) -> dict:
    """Query the LLM for an action decision. Returns {} if LLM disabled."""
    if not _LLM_ENABLED:
        return {}

    user_msg = json.dumps(observation, indent=2, default=str)
    messages.append({"role": "user", "content": user_msg})

    try:
        response = llm.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.1,
            max_tokens=200,
        )
        text = response.choices[0].message.content.strip()
        messages.append({"role": "assistant", "content": text})

        # Strip markdown code fences if present
        if text.startswith("```"):
            text = text.split("\n", 1)[-1]
        if text.endswith("```"):
            text = text.rsplit("```", 1)[0]
        text = text.strip()

        return json.loads(text)
    except json.JSONDecodeError as exc:
        log.warning("LLM returned invalid JSON: %s", exc)
        return {}
    except Exception as exc:
        log.warning("LLM call failed: %s", exc)
        return {}


def select_action(
    observation: dict,
    messages: list[dict],
    planner: HeuristicPlanner,
) -> dict:
    """LLM-primary action selection with heuristic fallback.

    1. Ask LLM for an action
    2. Validate it (correct type, valid target, affordable)
    3. If valid -> use LLM action
    4. If invalid -> fall back to heuristic
    """
    # LLM gets first try
    llm_action = ask_llm(messages, observation)

    if llm_action and _is_valid_llm_action(llm_action, observation):
        llm_action.setdefault("parameters", {})
        log.info(
            "  [LLM] %s(%s)",
            llm_action["action_type"],
            llm_action["target_shipment_id"],
        )
        return llm_action

    # Heuristic fallback
    h_action, explanation = planner.pick_action(observation)
    log.info(
        "  [HEURISTIC] %s(%s) — %s",
        h_action["action_type"],
        h_action["target_shipment_id"],
        explanation,
    )
    h_action.setdefault("parameters", {})
    return h_action


# ---------------------------------------------------------------------------
# Structured logging — [START], [STEP], [END] (hackathon-required format)
# ---------------------------------------------------------------------------

ENV_NAME = "mogul-logistics"


def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(
    step: int, action: str, reward: float, done: bool, error: object = None,
) -> None:
    print(
        f"[STEP] step={step} action={action} reward={reward} "
        f"done={done} error={error}",
        flush=True,
    )


def log_end(
    success: bool, steps: int, score: float, rewards: list[float],
) -> None:
    print(
        f"[END] success={success} steps={steps} score={score} "
        f"rewards={rewards}",
        flush=True,
    )


# ---------------------------------------------------------------------------
# Episode runner
# ---------------------------------------------------------------------------

async def run_episode(task_id: str) -> float:
    model_name = MODEL_NAME if _LLM_ENABLED else "heuristic-only"
    log_start(task=task_id, env=ENV_NAME, model=model_name)

    messages: list[dict] = [
        {"role": "system", "content": SYSTEM_PROMPT},
    ]
    planner = HeuristicPlanner()

    rewards: list[float] = []
    step_num = 0
    score = 0.0

    async with GenericEnvClient(base_url=ENV_URL) as env:
        result = await env.reset(task_id=task_id)
        obs = result.observation
        done = result.done

        while not done:
            action = select_action(obs, messages, planner)

            result = await env.step(action)
            obs = result.observation
            reward = result.reward or 0.0
            done = result.done
            step_num += 1

            rewards.append(reward)

            action_summary = (
                f"{action.get('action_type', '?')}"
                f"({action.get('target_shipment_id', '?')})"
            )
            log_step(
                step=step_num,
                action=action_summary,
                reward=reward,
                done=done,
                error=None,
            )

            if done:
                score = reward

    success = score >= 0.5
    log_end(success=success, steps=step_num, score=score, rewards=rewards)
    return score


async def main() -> None:
    start = time.time()
    scores: dict[str, float] = {}

    for task_id in TASKS:
        try:
            score = await run_episode(task_id)
            scores[task_id] = score
        except Exception as exc:
            log_end(success=False, steps=0, score=0.0, rewards=[])
            log.error("task=%s error=%s", task_id, exc)
            scores[task_id] = 0.0

    elapsed = time.time() - start
    print()
    print("=" * 50)
    print("RESULTS")
    print("=" * 50)
    for tid, sc in scores.items():
        print(f"  {tid}: {sc:.4f}")
    avg = sum(scores.values()) / max(len(scores), 1)
    print(f"  AVERAGE: {avg:.4f}")
    print(f"  TIME: {elapsed:.1f}s")


if __name__ == "__main__":
    asyncio.run(main())
