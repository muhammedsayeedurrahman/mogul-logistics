"""FastAPI application - entry point for the environment server."""

from __future__ import annotations

import sys
import traceback
from pathlib import Path

# Ensure project root is importable
_root = str(Path(__file__).resolve().parent.parent)
if _root not in sys.path:
    sys.path.insert(0, _root)

from fastapi.responses import RedirectResponse
from openenv.core.env_server import create_app

from models import ShipmentAction, ShipmentObservation
from server.constants import ACTION_COSTS, ACTION_PROGRESS, RESOLUTION_ACTIONS
from server.environment import ShipmentEnvironment

# Store dashboard build error for diagnostics
_dashboard_error: str | None = None

try:
    from server.gradio_custom import build_custom_dashboard
    _gradio_builder = build_custom_dashboard
except Exception as e:
    _dashboard_error = traceback.format_exc()
    _gradio_builder = None
    print(f"[WARN] Custom dashboard import failed: {e}", file=sys.stderr)


_builder_call_count = 0
_builder_args_info: str | None = None


def _safe_dashboard_builder(*args, **kwargs):
    """Wrapper that catches dashboard build errors for diagnostics."""
    global _dashboard_error, _builder_call_count, _builder_args_info
    _builder_call_count += 1
    _builder_args_info = f"args={len(args)}, kwargs={list(kwargs.keys())}"
    print(f"[DEBUG] Dashboard builder called (#{_builder_call_count}): {_builder_args_info}", file=sys.stderr)
    if _gradio_builder is None:
        _dashboard_error = f"Dashboard import failed (original error above)"
        raise RuntimeError(_dashboard_error)
    try:
        result = _gradio_builder(*args, **kwargs)
        print(f"[DEBUG] Dashboard builder succeeded, type={type(result).__name__}", file=sys.stderr)
        return result
    except Exception as e:
        _dashboard_error = traceback.format_exc()
        print(f"[WARN] Custom dashboard build failed:\n{_dashboard_error}", file=sys.stderr)
        raise


app = create_app(
    ShipmentEnvironment,
    ShipmentAction,
    ShipmentObservation,
    env_name="mogul-logistics",
    max_concurrent_envs=1,
    gradio_builder=_safe_dashboard_builder,
)


@app.get("/", include_in_schema=False)
async def root():
    """Redirect root to the web interface."""
    return RedirectResponse(url="/web")


@app.get("/debug/dashboard", tags=["Debug"])
async def debug_dashboard():
    """Show dashboard build error if any."""
    import gradio as gr
    return {
        "dashboard_error": _dashboard_error,
        "builder_available": _gradio_builder is not None,
        "builder_call_count": _builder_call_count,
        "builder_args_info": _builder_args_info,
        "gradio_version": gr.__version__,
    }


# ---------------------------------------------------------------------------
# API schema & MCP tools — agent-friendly discovery endpoints
# ---------------------------------------------------------------------------

_ACTION_DESCRIPTIONS: dict[str, str] = {
    "investigate": (
        "Investigate a shipment exception. Reveals exception details and "
        "enables resolution actions. Always do this first."
    ),
    "contact_carrier": (
        "Contact the shipping carrier for status updates. "
        "Low cost, small progress boost."
    ),
    "escalate": (
        "Escalate the issue to management for expedited review. "
        "Moderate cost, adds 20% progress."
    ),
    "file_claim": (
        "File an insurance or damage claim. Requires prior investigation. "
        "Can trigger resolution if progress reaches 100%."
    ),
    "reschedule": (
        "Reschedule the shipment for a new delivery window. "
        "Requires prior investigation. Good finishing action."
    ),
    "approve_refund": (
        "Approve a refund for the shipment exception. "
        "Requires prior investigation. Largest single progress boost."
    ),
    "reroute": (
        "Reroute the shipment through an alternative path. "
        "Requires prior investigation. High cost."
    ),
    "split_shipment": (
        "Split the shipment into multiple smaller shipments. "
        "Requires prior investigation. Most expensive action."
    ),
}

_ACTION_META = {
    action: {
        "cost": int(ACTION_COSTS[action]),
        "progress": ACTION_PROGRESS[action],
        "requires_investigation": action in RESOLUTION_ACTIONS,
        "is_resolution_action": action in RESOLUTION_ACTIONS,
        "description": _ACTION_DESCRIPTIONS[action],
    }
    for action in ACTION_COSTS
}


@app.get("/api/schema", tags=["Discovery"])
async def api_schema():
    """Full environment schema for agents and judges.

    Returns action space, observation format, grading rubric, and task definitions.
    """
    return {
        "name": "MOGUL Logistics",
        "version": "1.0.0",
        "description": (
            "Shipment exception resolution RL environment. An agent triages "
            "and resolves logistics exceptions (delays, damages, misroutes, "
            "customs holds) under time pressure and budget constraints."
        ),
        "action_space": _ACTION_META,
        "observation_fields": {
            "shipment_status": {
                "type": "string",
                "description": "Multi-line summary of all shipment statuses",
            },
            "exception_details": {
                "type": "string",
                "description": "Text description of active exceptions",
            },
            "available_actions": {
                "type": "array",
                "description": "List of valid action type strings",
            },
            "budget_remaining": {
                "type": "number",
                "description": "Remaining resolution budget in dollars",
            },
            "time_remaining": {
                "type": "integer",
                "description": "Steps remaining in the episode",
            },
            "resolution_progress": {
                "type": "object",
                "description": "Map of shipment_id -> progress (0.0 to 1.0)",
            },
            "feedback": {
                "type": "string",
                "description": "Human-readable result of the last action",
            },
            "done": {
                "type": "boolean",
                "description": "Whether the episode is complete",
            },
            "reward": {
                "type": "number",
                "description": "Reward signal; final composite score when done=True",
            },
        },
        "grading": {
            "resolution_rate": {
                "weight": 0.40,
                "formula": "resolved_exceptions / total_exceptions",
            },
            "cost_efficiency": {
                "weight": 0.25,
                "formula": "1 - (cost_spent / total_budget)",
            },
            "sla_compliance": {
                "weight": 0.20,
                "formula": "1 - (sla_violations / total_exceptions)",
            },
            "decision_quality": {
                "weight": 0.15,
                "formula": "0.6 * investigate_first_ratio + 0.4 * priority_order_ratio",
            },
        },
        "tasks": {
            "task_easy": {
                "ships": 1, "max_steps": 5, "budget": 5000,
                "difficulty": "Easy",
                "description": "Single delayed shipment, generous budget",
            },
            "task_medium": {
                "ships": 4, "max_steps": 10, "budget": 12000,
                "difficulty": "Medium",
                "description": "4 shipments with different exception types",
            },
            "task_hard": {
                "ships": 8, "max_steps": 15, "budget": 15000,
                "difficulty": "Hard",
                "description": "8 cascading failures from port closure, tight budget",
            },
        },
        "strategy_guide": {
            "3_step_fast_path": {
                "sequence": ["investigate", "approve_refund", "reschedule"],
                "cost": 2350,
                "description": "Fastest resolution — use when SLA is tight (≤3 steps)",
            },
            "4_step_cheap_path": {
                "sequence": ["investigate", "escalate", "file_claim", "reschedule"],
                "cost": 1350,
                "description": "Cheapest resolution — use when SLA allows (≥4 steps)",
            },
            "tips": [
                "Always investigate before resolution actions",
                "Work on ships with tightest SLA first",
                "Use 4-step cheap path when SLA allows (≥4 steps remaining)",
                "After resolving salvageable ships, investigate remaining for DQ points",
                "Act on higher-priority shipments first for better DQ score",
            ],
        },
    }


@app.get("/api/mcp/tools", tags=["MCP"])
async def mcp_tools():
    """MCP-compatible tool listing for AI agent discovery.

    Returns tools in Model Context Protocol format so LLM agents can
    discover and use the environment's action space programmatically.
    """
    tools = []
    for action_name, meta in _ACTION_META.items():
        tools.append({
            "name": action_name,
            "description": (
                f"{meta['description']} "
                f"Cost: ${meta['cost']:,}. Progress: +{meta['progress']:.0%}."
                + (" Requires investigation first." if meta["requires_investigation"] else "")
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "target_shipment_id": {
                        "type": "string",
                        "description": "Target shipment ID (e.g. SHP-001)",
                        "enum": [f"SHP-{i:03d}" for i in range(1, 9)],
                    },
                    "parameters": {
                        "type": "object",
                        "description": "Optional extra parameters",
                        "default": {},
                    },
                },
                "required": ["target_shipment_id"],
            },
        })
    return {"tools": tools}


def main() -> None:
    """Run the server directly via `python -m server.app` or `uv run server`."""
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
