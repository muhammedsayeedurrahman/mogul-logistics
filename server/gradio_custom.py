"""Custom Gradio dashboard for MOGUL Logistics environment.

Judge-friendly dashboard with sidebar controls, auto-run demo,
real-time reward chart, scorecard, and grading rubric.
"""

from __future__ import annotations

import asyncio
import json
import re
from typing import Any, Dict, List, Optional

import gradio as gr

from .graders import ACTION_COSTS

# ── Colour palette ──────────────────────────────────────────────────────
_BG      = "#0f1923"
_CARD_BG = "#162332"
_BORDER  = "#1e3a5f"
_TEXT    = "#e0e6ed"
_MUTED   = "#7a8ea0"
_GREEN   = "#00e676"
_YELLOW  = "#ffd740"
_RED     = "#ff5252"
_BLUE    = "#40c4ff"
_ORANGE  = "#ff9100"

# ── Force dark mode + transitions ───────────────────────────────────────
FORCE_DARK_JS = """
() => {
  document.body.classList.add('dark');
  document.querySelector('.gradio-container')?.classList.add('dark');
}
"""

CUSTOM_CSS = """
/* Root */
.mogul-root { background: #0f1923 !important; padding: 16px !important; }
.mogul-root * { color: #e0e6ed !important; }

/* Stat cards */
.stat-card {
  background: #162332 !important; border: 1px solid #1e3a5f !important;
  padding: 14px 18px !important; text-align: center !important;
  transition: border-color 0.3s ease, transform 0.2s ease !important;
}
.stat-card:hover { border-color: #40c4ff !important; transform: translateY(-2px) !important; }
.stat-card .stat-value {
  font-size: 1.8rem !important; font-weight: 700 !important; line-height: 1.2 !important;
}
.stat-card .stat-label {
  font-size: 0.72rem !important; text-transform: uppercase !important;
  letter-spacing: 0.08em !important; color: #7a8ea0 !important;
}
.stat-green .stat-value { color: #00e676 !important; }
.stat-blue  .stat-value { color: #40c4ff !important; }
.stat-yellow .stat-value { color: #ffd740 !important; }
.stat-red   .stat-value { color: #ff5252 !important; }

/* Action panel */
.action-panel {
  background: #162332 !important; border: 1px solid #1e3a5f !important;
  padding: 16px !important;
}

/* Buttons */
.btn-reset {
  background: linear-gradient(135deg, #1a3a5c, #0d2137) !important;
  border: 1px solid #40c4ff !important; color: #40c4ff !important;
}
.btn-step {
  background: linear-gradient(135deg, #00c853, #00e676) !important;
  border: none !important; color: #0f1923 !important; font-weight: 700 !important;
}
.btn-demo {
  background: linear-gradient(135deg, #ff6d00, #ff9100) !important;
  border: none !important; color: #0f1923 !important; font-weight: 700 !important;
  font-size: 1rem !important; padding: 12px !important;
}
.btn-demo-all {
  background: linear-gradient(135deg, #7c4dff, #b388ff) !important;
  border: none !important; color: #0f1923 !important; font-weight: 700 !important;
}

/* Log */
.action-log {
  background: #0d1520 !important; border: 1px solid #1e3a5f !important;
  font-family: 'JetBrains Mono', monospace !important; font-size: 0.78rem !important;
  max-height: 260px !important; overflow-y: auto !important;
}

/* Ship cards transition */
.ship-card-wrap div {
  transition: border-color 0.5s ease, background 0.3s ease !important;
}

/* Sidebar styling */
.sidebar-section {
  background: #162332 !important; border: 1px solid #1e3a5f !important;
  padding: 12px !important; margin-bottom: 8px !important; border-radius: 6px !important;
}
"""

# ── Task descriptions ───────────────────────────────────────────────────
TASK_INFO = {
    "Easy  -  1 ship, 5 steps, $5K": "task_easy",
    "Medium  -  4 ships, 10 steps, $12K": "task_medium",
    "Hard  -  8 ships, 15 steps, $15K": "task_hard",
}

# ── Heuristic for auto-run (mirrored from inference.py) ────────────────
_ACTION_PROGRESS = {
    "investigate": 0.15, "contact_carrier": 0.10, "escalate": 0.20,
    "reroute": 0.40, "reschedule": 0.35, "file_claim": 0.30,
    "approve_refund": 0.50, "split_shipment": 0.45,
}
_RESOLUTION_ACTIONS = {
    "reroute", "reschedule", "file_claim", "approve_refund", "split_shipment",
}
_PRIORITY_RANK = {"critical": 0, "high": 1, "medium": 2, "low": 3}

_SHIP_RE = re.compile(
    r"(SHP-\d+):\s+\S+\s+\|\s+status=(\w+)\s+\|\s+priority=(\w+)"
    r"\s+\|\s+progress=(\d+)%\s+\|\s+SLA in (\d+) steps"
)


def _parse_ships(status_text: str) -> list[dict]:
    ships = []
    for m in _SHIP_RE.finditer(status_text):
        ships.append({
            "id": m.group(1), "status": m.group(2),
            "priority": m.group(3),
            "progress": int(m.group(4)) / 100.0,
            "sla": int(m.group(5)),
        })
    return ships


def _demo_heuristic(obs: dict) -> tuple[dict, str]:
    """Pick next action + return human-readable explanation."""
    status_text = obs.get("shipment_status", "")
    budget = obs.get("budget_remaining", 0)
    ships = _parse_ships(status_text)
    active = [s for s in ships if s["status"] not in ("resolved", "failed")]

    if not active:
        return (
            {"action_type": "investigate", "target_shipment_id": "SHP-001", "parameters": {}},
            "No active shipments remaining.",
        )

    # Continue in-progress ship
    in_progress = [s for s in active if s["progress"] > 0.001]
    if in_progress:
        target = max(in_progress, key=lambda s: s["progress"])
        reason = f"Continuing {target['id']} (progress {target['progress']:.0%})"
    else:
        for s in active:
            inv = s["progress"] >= 0.14 or s["status"] in ("investigating", "action_taken")
            s["min_steps"] = 1 if (s["progress"] >= 0.50 and inv) else (2 if inv else 3)
            s["salvageable"] = s["sla"] >= s["min_steps"]
        salvageable = [s for s in active if s.get("salvageable")]
        if salvageable:
            salvageable.sort(key=lambda s: (s["sla"], _PRIORITY_RANK.get(s["priority"], 3)))
            target = salvageable[0]
            reason = f"Starting {target['id']} (SLA={target['sla']}, {target['priority']} priority)"
        else:
            active.sort(key=lambda s: _PRIORITY_RANK.get(s["priority"], 3))
            target = active[0]
            if budget >= 50 and target["progress"] < 0.001:
                return (
                    {"action_type": "investigate", "target_shipment_id": target["id"], "parameters": {}},
                    f"DQ farming: investigating {target['id']} ({target['priority']}) for decision quality points",
                )
            return (
                {"action_type": "contact_carrier", "target_shipment_id": target["id"], "parameters": {}},
                f"All ships doomed — contacting carrier for {target['id']}",
            )

    sid = target["id"]
    prog = target["progress"]
    investigated = prog >= 0.14 or target["status"] in ("investigating", "action_taken")

    if prog < 0.001 and budget >= 50:
        return (
            {"action_type": "investigate", "target_shipment_id": sid, "parameters": {}},
            f"{reason} -> Investigating first (required before resolution)",
        )

    needed = 1.0 - prog
    if investigated:
        for atype in ["reschedule", "file_claim", "approve_refund"]:
            if _ACTION_PROGRESS[atype] >= needed and int(ACTION_COSTS.get(atype, 9999)) <= budget:
                return (
                    {"action_type": atype, "target_shipment_id": sid, "parameters": {}},
                    f"{reason} -> {atype} will finish it ({_ACTION_PROGRESS[atype]:.0%} >= {needed:.0%} needed)",
                )
        if prog < 0.50 and budget >= 1500:
            return (
                {"action_type": "approve_refund", "target_shipment_id": sid, "parameters": {}},
                f"{reason} -> approve_refund adds 50% progress (fast path)",
            )
        if budget >= 800:
            return (
                {"action_type": "reschedule", "target_shipment_id": sid, "parameters": {}},
                f"{reason} -> reschedule adds 35% progress",
            )

    if not investigated and budget >= 50:
        return (
            {"action_type": "investigate", "target_shipment_id": sid, "parameters": {}},
            f"{reason} -> Must investigate before resolution actions",
        )

    return (
        {"action_type": "contact_carrier", "target_shipment_id": sid, "parameters": {}},
        f"{reason} -> Low budget, contacting carrier",
    )


# ── Rendering helpers ───────────────────────────────────────────────────
_PRIO_ICON = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}


def _progress_bar(pct: float, width: int = 20) -> str:
    filled = int(pct * width)
    empty = width - filled
    colour = _GREEN if pct >= 1.0 else (_YELLOW if pct >= 0.5 else _BLUE)
    return (
        f'<span style="color:{colour}">{"█" * filled}</span>'
        f'<span style="color:#1e3a5f">{"░" * empty}</span>'
        f' {pct:.0%}'
    )


def _sla_badge(steps: int) -> str:
    if steps <= 1:
        return f'<span style="color:{_RED};font-weight:700">⚠ SLA {steps}</span>'
    if steps <= 3:
        return f'<span style="color:{_YELLOW}">SLA {steps}</span>'
    return f'<span style="color:{_GREEN}">SLA {steps}</span>'


def _status_colour(status: str) -> str:
    return {
        "resolved": _GREEN, "failed": _RED, "investigating": _BLUE,
        "action_taken": _ORANGE, "new": _MUTED,
    }.get(status, _MUTED)


def _render_shipments(obs: dict) -> str:
    status_text = obs.get("shipment_status", "")
    progress_map = obs.get("resolution_progress", {})
    if not status_text or status_text == "No active shipments.":
        return (
            '<div style="text-align:center;padding:40px;color:#7a8ea0">'
            '<div style="font-size:2rem;margin-bottom:8px">📦</div>'
            'No active shipments — select a difficulty and click '
            '<b>Run Agent Demo</b> to start.</div>'
        )

    cards: list[str] = []
    for row in status_text.strip().split("\n"):
        row = row.strip()
        if not row:
            continue
        parts = [p.strip() for p in row.split("|")]
        if len(parts) < 5:
            continue

        sid = parts[0].split(":")[0].strip()
        exc_type = parts[0].split(":", 1)[1].strip() if ":" in parts[0] else "unknown"
        status_val = parts[1].replace("status=", "").strip()
        priority = parts[2].replace("priority=", "").strip()
        prog = progress_map.get(sid, 0.0)
        sla_steps = int("".join(c for c in parts[4] if c.isdigit()) or "0")

        col = _status_colour(status_val)
        icon = _PRIO_ICON.get(priority, "")
        inv = (
            ' <span style="background:#1a3a5c;color:#40c4ff;'
            'padding:1px 6px;font-size:0.6rem;border-radius:3px">✓ INVESTIGATED</span>'
            if status_val in ("investigating", "action_taken") else ""
        )
        resolved_glow = "box-shadow:0 0 12px rgba(0,230,118,0.3);" if status_val == "resolved" else ""
        failed_dim = "opacity:0.6;" if status_val == "failed" else ""

        cards.append(
            f'<div style="background:#162332;border:1px solid #1e3a5f;'
            f'border-left:3px solid {col};padding:10px 14px;margin-bottom:6px;'
            f'border-radius:4px;transition:all 0.3s ease;{resolved_glow}{failed_dim}">'
            f'<div style="display:flex;justify-content:space-between;align-items:center">'
            f'  <span style="font-weight:700;font-size:0.95rem">{sid}{inv}</span>'
            f'  <span style="font-size:0.72rem;color:{col};text-transform:uppercase;'
            f'font-weight:600">{status_val}</span></div>'
            f'<div style="font-size:0.78rem;color:#7a8ea0;margin:4px 0">'
            f'{icon} {priority} &middot; {exc_type}</div>'
            f'<div style="margin-top:6px">{_progress_bar(prog)}</div>'
            f'<div style="text-align:right;margin-top:4px;font-size:0.72rem">'
            f'{_sla_badge(sla_steps)}</div></div>'
        )
    return "\n".join(cards)


def _render_stats(obs: dict) -> tuple[str, str, str, str]:
    pm = obs.get("resolution_progress", {})
    total = len(pm)
    resolved = sum(1 for v in pm.values() if v >= 1.0)
    budget = obs.get("budget_remaining", 0)
    time_left = obs.get("time_remaining", 0)
    failed = obs.get("shipment_status", "").count("status=failed")
    return (f"{resolved}/{total}", f"${budget:,.0f}", str(time_left), str(failed))


def _render_scorecard(data: dict) -> str:
    obs = data.get("observation", {})
    reward = data.get("reward", 0.0)
    if not data.get("done"):
        return ""

    pm = obs.get("resolution_progress", {})
    total = max(len(pm), 1)
    resolved = sum(1 for v in pm.values() if v >= 1.0)
    score = reward or 0.0
    score_col = _GREEN if score >= 0.8 else (_YELLOW if score >= 0.6 else _RED)

    # Component estimates
    res_s = (resolved / total) * 0.4

    def _bar(val: float, mx: float, col: str, label: str) -> str:
        pct = min(val / max(mx, 0.001), 1.0) * 100
        return (
            f'<div style="margin:8px 0">'
            f'<div style="display:flex;justify-content:space-between;font-size:0.78rem">'
            f'<span>{label}</span><span style="color:{col}">{val:.4f}</span></div>'
            f'<div style="background:#1e3a5f;height:12px;border-radius:6px;overflow:hidden">'
            f'<div style="background:{col};height:100%;width:{pct:.1f}%;'
            f'border-radius:6px;transition:width 0.5s ease"></div></div></div>'
        )

    bars = (
        _bar(res_s, 0.40, _GREEN, f"Resolution Rate ({resolved}/{total})")
        + _bar(min(0.25, max(0, score - res_s)), 0.25, _BLUE, "Cost Efficiency")
        + _bar(0.20, 0.20, _YELLOW, "SLA Compliance")
        + _bar(max(0, score - res_s - 0.25 - 0.20), 0.15, _ORANGE, "Decision Quality")
    )

    # Per-shipment table
    rows = ""
    status_text = obs.get("shipment_status", "")
    for row in status_text.strip().split("\n"):
        row = row.strip()
        if not row:
            continue
        parts = [p.strip() for p in row.split("|")]
        if len(parts) < 5:
            continue
        sid = parts[0].split(":")[0].strip()
        st = parts[1].replace("status=", "").strip()
        p = pm.get(sid, 0.0)
        sc = _status_colour(st)
        rows += (
            f'<tr style="border-bottom:1px solid #1e3a5f">'
            f'<td style="padding:6px 8px">{sid}</td>'
            f'<td style="padding:6px 8px;color:{sc};font-weight:600">{st.upper()}</td>'
            f'<td style="padding:6px 8px">{p:.0%}</td></tr>'
        )

    return (
        f'<div style="background:linear-gradient(135deg,#0d2137,#162332);'
        f'border:2px solid {score_col};padding:24px;margin-top:16px;border-radius:12px;'
        f'box-shadow:0 0 20px rgba(0,0,0,0.5)">'
        f'<div style="text-align:center;margin-bottom:20px">'
        f'<div style="font-size:0.7rem;color:#7a8ea0;text-transform:uppercase;'
        f'letter-spacing:0.15em;margin-bottom:4px">FINAL SCORE</div>'
        f'<div style="font-size:3.5rem;font-weight:800;color:{score_col};'
        f'text-shadow:0 0 20px {score_col}40">{score:.4f}</div></div>'
        f'<div style="max-width:500px;margin:0 auto">{bars}</div>'
        f'<div style="margin-top:20px">'
        f'<div style="font-size:0.7rem;color:#7a8ea0;text-transform:uppercase;'
        f'letter-spacing:0.1em;margin-bottom:8px">SHIPMENT OUTCOMES</div>'
        f'<table style="width:100%;font-size:0.82rem;border-collapse:collapse">'
        f'<tr style="color:#7a8ea0;border-bottom:1px solid #1e3a5f">'
        f'<th style="padding:6px 8px;text-align:left">ID</th>'
        f'<th style="padding:6px 8px;text-align:left">Status</th>'
        f'<th style="padding:6px 8px;text-align:left">Progress</th></tr>'
        f'{rows}</table></div></div>'
    )


RUBRIC_HTML = """
<div style="background:#162332;border:1px solid #1e3a5f;padding:16px;border-radius:8px;font-size:0.82rem">
<table style="width:100%;border-collapse:collapse">
<tr style="border-bottom:1px solid #1e3a5f;color:#7a8ea0">
  <th style="padding:8px;text-align:left">Component</th>
  <th style="padding:8px;text-align:center">Weight</th>
  <th style="padding:8px;text-align:left">Formula</th></tr>
<tr style="border-bottom:1px solid #1e3a5f">
  <td style="padding:8px"><span style="color:#00e676">●</span> Resolution Rate</td>
  <td style="padding:8px;text-align:center;font-weight:700">40%</td>
  <td style="padding:8px;color:#7a8ea0">resolved_exceptions / total</td></tr>
<tr style="border-bottom:1px solid #1e3a5f">
  <td style="padding:8px"><span style="color:#40c4ff">●</span> Cost Efficiency</td>
  <td style="padding:8px;text-align:center;font-weight:700">25%</td>
  <td style="padding:8px;color:#7a8ea0">1 - (cost_spent / budget)</td></tr>
<tr style="border-bottom:1px solid #1e3a5f">
  <td style="padding:8px"><span style="color:#ffd740">●</span> SLA Compliance</td>
  <td style="padding:8px;text-align:center;font-weight:700">20%</td>
  <td style="padding:8px;color:#7a8ea0">1 - (violations / total)</td></tr>
<tr>
  <td style="padding:8px"><span style="color:#ff9100">●</span> Decision Quality</td>
  <td style="padding:8px;text-align:center;font-weight:700">15%</td>
  <td style="padding:8px;color:#7a8ea0">investigate-first + priority order</td></tr>
</table>
<div style="margin-top:12px;padding-top:12px;border-top:1px solid #1e3a5f;color:#7a8ea0;font-size:0.75rem">
<b style="color:#e0e6ed">Optimal 3-step sequence:</b> investigate ($50) → approve_refund ($1,500) → reschedule ($800) = 100% resolved<br>
<b style="color:#e0e6ed">Resolution actions:</b> reroute, reschedule, file_claim, approve_refund, split_shipment — only these can mark a shipment as resolved
</div>
</div>
"""

HOW_IT_WORKS_HTML = """
<div style="background:linear-gradient(135deg,#0d2137,#1a3a5c);border:1px solid #1e3a5f;
padding:20px;border-radius:8px;margin-bottom:16px">
<h2 style="margin:0 0 12px 0;font-size:1.1rem;color:#40c4ff">📦 How MOGUL Logistics Works</h2>
<div style="font-size:0.85rem;line-height:1.6;color:#c8d6e0">
An <b>RL agent</b> resolves logistics shipment exceptions (delays, damages, misroutes, customs holds)
under <b>time pressure</b> (SLA deadlines) and <b>budget constraints</b>.<br><br>

<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:8px">
<div style="background:#16233280;padding:10px;border-radius:6px;border:1px solid #1e3a5f">
<div style="color:#00e676;font-weight:700;font-size:0.78rem;margin-bottom:4px">🎯 GOAL</div>
Resolve as many shipments as possible before SLA deadlines expire, while staying under budget.
</div>
<div style="background:#16233280;padding:10px;border-radius:6px;border:1px solid #1e3a5f">
<div style="color:#ff9100;font-weight:700;font-size:0.78rem;margin-bottom:4px">⚡ CHALLENGE</div>
Each step costs time — ALL active shipments' SLA deadlines tick down by 1 every step.
</div>
</div>

<div style="margin-top:12px;padding:10px;background:#16233280;border-radius:6px;border:1px solid #1e3a5f">
<div style="color:#ffd740;font-weight:700;font-size:0.78rem;margin-bottom:4px">🔧 AGENT STRATEGY</div>
<code style="color:#40c4ff">investigate</code> ($50) →
<code style="color:#40c4ff">approve_refund</code> ($1,500) →
<code style="color:#40c4ff">reschedule</code> ($800) = <span style="color:#00e676;font-weight:700">100% resolved in 3 steps</span>
</div>
</div></div>
"""

INTRO_HTML = """
<div style="background:linear-gradient(135deg,#0d2137 0%,#1a3a5c 100%);
border:1px solid #1e3a5f;padding:20px 24px;margin-bottom:16px;border-radius:8px">
<div style="display:flex;justify-content:space-between;align-items:center">
<div>
<h1 style="margin:0;font-size:1.6rem;color:#e0e6ed;letter-spacing:-0.02em">MOGUL Logistics</h1>
<div style="color:#7a8ea0;font-size:0.82rem;margin-top:4px">
Shipment Exception Resolution — RL Environment</div>
</div>
<div style="text-align:right">
<div style="color:#40c4ff;font-size:0.82rem;font-weight:600">OpenEnv Hackathon</div>
<div style="color:#7a8ea0;font-size:0.72rem">v1.0.0 · Muhammed Sayeedur Rahman</div>
</div></div></div>
"""


# ── Builder ─────────────────────────────────────────────────────────────

def build_custom_dashboard(
    web_manager: Any,
    action_fields: List[Dict[str, Any]],
    metadata: Any,
    is_chat_env: bool,
    title: str,
    quick_start_md: Optional[str],
) -> gr.Blocks:
    """Build a logistics-themed Gradio dashboard with sidebar controls."""

    action_log_entries: list[str] = []
    step_counter: list[int] = [0]
    reward_history: list[dict] = []

    # ── Core handlers ───────────────────────────────────────────────

    def _task_id(label: str) -> str:
        return TASK_INFO.get(label, "task_easy")

    def _wrap(text: str) -> str:
        return (
            f'<div style="background:#0d2137;border:1px solid #1e3a5f;'
            f'padding:12px 16px;border-radius:6px;font-family:monospace;'
            f'font-size:0.82rem;color:#40c4ff;white-space:pre-wrap">'
            f'{text}</div>'
        )

    async def do_reset(task_label):
        action_log_entries.clear()
        reward_history.clear()
        step_counter[0] = 0
        tid = _task_id(task_label)
        data = await web_manager.reset_environment(reset_kwargs={"task_id": tid})
        obs = data.get("observation", {})
        return (
            _render_shipments(obs),
            *_render_stats(obs),
            _wrap(obs.get("feedback", "Episode started.")),
            "",
            json.dumps(data, indent=2),
            "",  # scorecard
            "",  # narration
        )

    async def do_step(action_type, target_id, params_str):
        params = {}
        if params_str and params_str.strip():
            try:
                params = json.loads(params_str)
            except json.JSONDecodeError:
                pass

        data = await web_manager.step_environment({
            "action_type": action_type,
            "target_shipment_id": target_id,
            "parameters": params,
        })
        obs = data.get("observation", {})
        reward = data.get("reward")
        done = data.get("done", False)

        step_counter[0] += 1
        cost = int(ACTION_COSTS.get(action_type, 0))
        entry = f"[Step {step_counter[0]}] {action_type}({target_id}) ${cost:,}"
        if reward is not None:
            entry += f"  r={reward:.4f}"
        if done:
            entry += "  ✓ DONE"
        action_log_entries.append(entry)

        scorecard = _render_scorecard(data) if done else ""
        return (
            _render_shipments(obs),
            *_render_stats(obs),
            _wrap(obs.get("feedback", "")),
            "\n".join(action_log_entries),
            json.dumps(data, indent=2),
            scorecard,
            "",  # narration
        )

    async def do_auto_run(task_label, speed):
        """Step-by-step auto-run with narration."""
        action_log_entries.clear()
        reward_history.clear()
        step_counter[0] = 0
        tid = _task_id(task_label)

        data = await web_manager.reset_environment(reset_kwargs={"task_id": tid})
        obs = data.get("observation", {})
        narration = f"🟢 Episode started — {task_label}"
        yield (
            _render_shipments(obs),
            *_render_stats(obs),
            _wrap(obs.get("feedback", "Episode started.")),
            "",
            json.dumps(data, indent=2),
            "",
            _wrap(narration),
        )

        done = data.get("done", False)
        while not done:
            delay = max(0.2, min(3.0, speed))
            await asyncio.sleep(delay)

            action, explanation = _demo_heuristic(obs)
            data = await web_manager.step_environment({
                "action_type": action["action_type"],
                "target_shipment_id": action["target_shipment_id"],
                "parameters": action.get("parameters", {}),
            })
            obs = data.get("observation", {})
            reward = data.get("reward")
            done = data.get("done", False)

            step_counter[0] += 1
            cost = int(ACTION_COSTS.get(action["action_type"], 0))
            entry = (
                f"[Step {step_counter[0]}] "
                f"{action['action_type']}({action['target_shipment_id']}) "
                f"${cost:,}"
            )
            if reward is not None:
                entry += f"  r={reward:.4f}"
            if done:
                entry += "  ✓ DONE"
            action_log_entries.append(entry)
            scorecard = _render_scorecard(data) if done else ""

            narration = f"Step {step_counter[0]}: {explanation}"
            if done:
                narration += f"\n\n🏁 Episode complete — Final score: {reward:.4f}"

            yield (
                _render_shipments(obs),
                *_render_stats(obs),
                _wrap(obs.get("feedback", "")),
                "\n".join(action_log_entries),
                json.dumps(data, indent=2),
                scorecard,
                _wrap(narration),
            )

    async def do_run_all(speed):
        """Run all 3 difficulties sequentially and show comparison."""
        results = {}
        for label, tid in TASK_INFO.items():
            action_log_entries.clear()
            step_counter[0] = 0

            data = await web_manager.reset_environment(reset_kwargs={"task_id": tid})
            obs = data.get("observation", {})
            done = data.get("done", False)

            while not done:
                await asyncio.sleep(0.05)  # Fast for comparison
                action, _ = _demo_heuristic(obs)
                data = await web_manager.step_environment({
                    "action_type": action["action_type"],
                    "target_shipment_id": action["target_shipment_id"],
                    "parameters": action.get("parameters", {}),
                })
                obs = data.get("observation", {})
                done = data.get("done", False)

            score = data.get("reward", 0.0)
            results[label] = score

        # Build comparison card
        rows = ""
        for label, score in results.items():
            col = _GREEN if score >= 0.7 else (_YELLOW if score >= 0.5 else _RED)
            bar_w = score * 100
            rows += (
                f'<div style="margin:8px 0">'
                f'<div style="display:flex;justify-content:space-between;'
                f'font-size:0.85rem;margin-bottom:4px">'
                f'<span>{label.split("-")[0].strip()}</span>'
                f'<span style="color:{col};font-weight:700">{score:.4f}</span></div>'
                f'<div style="background:#1e3a5f;height:16px;border-radius:8px;overflow:hidden">'
                f'<div style="background:{col};height:100%;width:{bar_w:.1f}%;'
                f'border-radius:8px;transition:width 0.5s ease"></div></div></div>'
            )

        avg = sum(results.values()) / max(len(results), 1)
        avg_col = _GREEN if avg >= 0.7 else (_YELLOW if avg >= 0.5 else _RED)

        comparison = (
            f'<div style="background:linear-gradient(135deg,#0d2137,#162332);'
            f'border:2px solid {avg_col};padding:24px;border-radius:12px;'
            f'box-shadow:0 0 20px rgba(0,0,0,0.5)">'
            f'<div style="text-align:center;margin-bottom:16px">'
            f'<div style="font-size:0.7rem;color:#7a8ea0;text-transform:uppercase;'
            f'letter-spacing:0.15em">AVERAGE SCORE</div>'
            f'<div style="font-size:3rem;font-weight:800;color:{avg_col};'
            f'text-shadow:0 0 20px {avg_col}40">{avg:.4f}</div></div>'
            f'{rows}</div>'
        )

        return comparison

    # ── Build the dashboard ─────────────────────────────────────────

    # Tab-hiding CSS — injected via gr.HTML, applies globally to hide
    # the Playground/Custom tab bar and force Custom content visible.
    _TAB_OVERRIDE_CSS = """
    .tabs > .tab-nav { display: none !important; }
    .tabitem { display: none !important; }
    .tabitem:last-of-type { display: block !important; }
    """

    # JS to auto-switch to Custom tab and enable dark mode
    _AUTO_SWITCH_JS = """
    () => {
      document.body.classList.add('dark');
      var gc = document.querySelector('.gradio-container');
      if (gc) gc.classList.add('dark');
      setTimeout(function() {
        var tabs = document.querySelectorAll('button[role="tab"]');
        tabs.forEach(function(t) {
          if (t.textContent.trim() === 'Custom') t.click();
        });
      }, 600);
    }
    """

    with gr.Blocks() as dashboard:

        # Inject CSS (works even inside hidden tab — browsers still parse <style>)
        gr.HTML(f"<style>{CUSTOM_CSS}\n{_TAB_OVERRIDE_CSS}</style>")

        # ── Sidebar: controls ──
        with gr.Sidebar(position="left", open=True):
            gr.HTML(
                '<div style="font-size:1.1rem;font-weight:700;color:#40c4ff;'
                'margin-bottom:12px">⚙ Controls</div>'
            )

            task_selector = gr.Dropdown(
                choices=list(TASK_INFO.keys()),
                value=list(TASK_INFO.keys())[0],
                label="Difficulty",
            )

            demo_btn = gr.Button(
                "▶  Run Agent Demo",
                variant="primary",
                elem_classes="btn-demo",
            )

            speed_slider = gr.Slider(
                minimum=0.3, maximum=2.0, value=0.8, step=0.1,
                label="Demo Speed (seconds per step)",
            )

            gr.HTML('<hr style="border-color:#1e3a5f;margin:12px 0">')

            run_all_btn = gr.Button(
                "⚡ Run All Difficulties",
                variant="secondary",
                elem_classes="btn-demo-all",
            )

            gr.HTML('<hr style="border-color:#1e3a5f;margin:12px 0">')

            with gr.Accordion("📋 Grading Rubric", open=False):
                gr.HTML(RUBRIC_HTML)

            with gr.Accordion("🔧 Manual Actions", open=False):
                action_type = gr.Dropdown(
                    choices=sorted(ACTION_COSTS.keys()),
                    label="Action Type", value="investigate",
                )
                target_id = gr.Dropdown(
                    choices=[f"SHP-{i:03d}" for i in range(1, 9)],
                    label="Target Shipment", value="SHP-001",
                )
                params_input = gr.Textbox(
                    label="Parameters (JSON)", value="{}",
                    placeholder='{"reason": "urgent"}',
                )
                cost_hint = gr.HTML(
                    f'<div style="font-size:0.78rem;color:#7a8ea0">'
                    f'Cost: <span style="color:#ffd740">'
                    f'${int(ACTION_COSTS.get("investigate", 0)):,}</span></div>'
                )

                def _update_cost(at):
                    c = int(ACTION_COSTS.get(at, 0))
                    return (
                        f'<div style="font-size:0.78rem;color:#7a8ea0">'
                        f'Cost: <span style="color:#ffd740">${c:,}</span></div>'
                    )

                action_type.change(fn=_update_cost, inputs=[action_type], outputs=[cost_hint])

                with gr.Row():
                    step_btn = gr.Button("Execute", variant="primary", elem_classes="btn-step")
                    reset_btn = gr.Button("Reset", variant="secondary", elem_classes="btn-reset")

        # ── Main content ──
        with gr.Column(elem_classes="mogul-root"):

            # Header
            gr.HTML(INTRO_HTML)

            # How it works
            gr.HTML(HOW_IT_WORKS_HTML)

            # Stats row
            with gr.Row():
                stat_resolved = gr.Textbox(
                    value="0/0", label="RESOLVED", interactive=False,
                    elem_classes="stat-card stat-green",
                )
                stat_budget = gr.Textbox(
                    value="$0", label="BUDGET", interactive=False,
                    elem_classes="stat-card stat-blue",
                )
                stat_time = gr.Textbox(
                    value="0", label="STEPS LEFT", interactive=False,
                    elem_classes="stat-card stat-yellow",
                )
                stat_sla = gr.Textbox(
                    value="0", label="SLA VIOLATIONS", interactive=False,
                    elem_classes="stat-card stat-red",
                )

            # Agent narration
            narration_display = gr.HTML(value="")

            # Shipments
            with gr.Row():
                with gr.Column(scale=3):
                    gr.HTML(
                        '<div style="color:#7a8ea0;font-size:0.72rem;'
                        'text-transform:uppercase;letter-spacing:0.1em;'
                        'margin-bottom:6px">Shipments</div>'
                    )
                    shipments_display = gr.HTML(
                        value=(
                            '<div style="text-align:center;padding:40px;color:#7a8ea0">'
                            '<div style="font-size:2rem;margin-bottom:8px">📦</div>'
                            'Select a difficulty and click <b>▶ Run Agent Demo</b> '
                            'in the sidebar to watch the agent work.</div>'
                        ),
                    )

                with gr.Column(scale=2):
                    gr.HTML(
                        '<div style="color:#7a8ea0;font-size:0.72rem;'
                        'text-transform:uppercase;letter-spacing:0.1em;'
                        'margin-bottom:6px">Feedback</div>'
                    )
                    feedback_display = gr.HTML(
                        value=(
                            '<div style="background:#0d2137;border:1px solid #1e3a5f;'
                            'padding:12px 16px;border-radius:6px;font-family:monospace;'
                            'font-size:0.82rem;color:#40c4ff">Ready.</div>'
                        ),
                    )

                    gr.HTML(
                        '<div style="color:#7a8ea0;font-size:0.72rem;'
                        'text-transform:uppercase;letter-spacing:0.1em;'
                        'margin:8px 0 6px 0">Action Log</div>'
                    )
                    log_display = gr.Textbox(
                        value="", interactive=False, lines=6,
                        elem_classes="action-log",
                    )

            # Scorecard
            scorecard_display = gr.HTML(value="")

            # Run All comparison
            comparison_display = gr.HTML(value="")

            # Raw JSON
            with gr.Accordion("📄 Raw JSON Response", open=False):
                raw_json = gr.Code(value="", language="json", interactive=False)

        # ── Wiring ──────────────────────────────────────────────────

        main_outputs = [
            shipments_display,
            stat_resolved, stat_budget, stat_time, stat_sla,
            feedback_display,
            log_display,
            raw_json,
            scorecard_display,
            narration_display,
        ]

        async def reset_wrap(task_label):
            r = list(await do_reset(task_label))
            return r

        async def step_wrap(at, tid, params):
            r = list(await do_step(at, tid, params))
            return r

        async def demo_wrap(task_label, speed):
            async for r in do_auto_run(task_label, speed):
                yield list(r)

        reset_btn.click(fn=reset_wrap, inputs=[task_selector], outputs=main_outputs)
        step_btn.click(
            fn=step_wrap,
            inputs=[action_type, target_id, params_input],
            outputs=main_outputs,
        )
        demo_btn.click(
            fn=demo_wrap,
            inputs=[task_selector, speed_slider],
            outputs=main_outputs,
        )
        run_all_btn.click(
            fn=do_run_all,
            inputs=[speed_slider],
            outputs=[comparison_display],
        )

        # Auto-switch to Custom tab + dark mode on load
        dashboard.load(fn=None, js=_AUTO_SWITCH_JS)

    return dashboard
