"""CSS, HTML templates, and render helpers for the Gradio dashboard.

Extracted from gradio_custom.py to keep the builder file focused on
layout and interaction.
"""

from __future__ import annotations

from .constants import ACTION_COSTS

# ── Colour palette ──────────────────────────────────────────────────────
_BG      = "#1c1c1c"
_CARD_BG = "#262626"
_BORDER  = "#404040"
_TEXT    = "#e0e6ed"
_MUTED   = "#666666"
_GREEN   = "#2B7D6D"
_YELLOW  = "#ffd740"
_RED     = "#ff5252"
_BLUE    = "#0668E1"
_ORANGE  = "#EE4C2C"

# ── Task descriptions ───────────────────────────────────────────────────
TASK_INFO = {
    "Easy  -  1 ship, 5 steps, $5K": "task_easy",
    "Medium  -  4 ships, 10 steps, $12K": "task_medium",
    "Hard  -  8 ships, 15 steps, $15K": "task_hard",
}

# ── Icon / colour maps ─────────────────────────────────────────────────
ACTION_ICONS = {
    "investigate": "\U0001f50d", "contact_carrier": "\U0001f4de",
    "escalate": "\u2b06\ufe0f", "reroute": "\U0001f504",
    "reschedule": "\U0001f4c5", "file_claim": "\U0001f4cb",
    "approve_refund": "\U0001f4b0", "split_shipment": "\u2702\ufe0f",
    "reset": "\U0001f680",
}
ACTION_COLORS = {
    "investigate": "#0668E1", "contact_carrier": "#666666",
    "escalate": "#EE4C2C", "reroute": "#812CE5",
    "reschedule": "#ffd740", "file_claim": "#ff5252",
    "approve_refund": "#2B7D6D", "split_shipment": "#EE4C2C",
    "reset": "#0668E1",
}
_PRIO_ICON = {"critical": "\U0001f534", "high": "\U0001f7e0", "medium": "\U0001f7e1", "low": "\U0001f7e2"}

# ── CSS ─────────────────────────────────────────────────────────────────
CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

/* Root */
.mogul-root { background: #1c1c1c !important; padding: 16px !important; font-family: 'Inter', sans-serif !important; }
.mogul-root * { color: #e0e6ed !important; font-family: 'Inter', sans-serif; }

/* Stat cards */
.stat-card {
  background: #262626 !important; border: 1px solid #404040 !important;
  padding: 14px 18px !important; text-align: center !important;
  transition: border-color 0.3s ease, transform 0.2s ease, box-shadow 0.3s ease !important;
  border-radius: 8px !important;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2) !important;
}
.stat-card:hover { border-color: #0668E1 !important; transform: translateY(-2px) !important; }
.stat-card .stat-value {
  font-size: 1.8rem !important; font-weight: 700 !important; line-height: 1.2 !important;
}
.stat-card .stat-label {
  font-size: 0.72rem !important; text-transform: uppercase !important;
  letter-spacing: 0.08em !important; color: #666666 !important;
}
.stat-green .stat-value { color: #2B7D6D !important; text-shadow: 0 0 10px rgba(43, 125, 109, 0.4) !important;}
.stat-blue  .stat-value { color: #0668E1 !important; }
.stat-yellow .stat-value { color: #ffd740 !important; }
.stat-red   .stat-value { color: #ff5252 !important; }

/* Action panel */
.action-panel {
  background: #262626 !important; border: 1px solid #404040 !important;
  padding: 16px !important; border-radius: 8px !important;
}

/* Buttons */
.btn-reset {
  background: linear-gradient(135deg, #1c1c1c, #262626) !important;
  border: 1px solid #0668E1 !important; color: #0668E1 !important;
}
.btn-step {
  background: linear-gradient(135deg, #2B7D6D, #1f5a4e) !important;
  border: none !important; color: #ffffff !important; font-weight: 700 !important;
}
.btn-demo {
  background: linear-gradient(135deg, #0668E1, #EE4C2C) !important;
  border: none !important; color: #ffffff !important; font-weight: 700 !important;
  font-size: 1rem !important; padding: 12px !important;
  box-shadow: 0 0 10px rgba(238, 76, 44, 0.4) !important;
}
.btn-demo-all {
  background: linear-gradient(135deg, #812CE5, #5a1e9e) !important;
  border: none !important; color: #ffffff !important; font-weight: 700 !important;
  box-shadow: 0 0 10px rgba(129, 44, 229, 0.4) !important;
}

/* Log */
.action-log {
  background: #1c1c1c !important; border: 1px solid #404040 !important;
  font-family: 'JetBrains Mono', monospace !important; font-size: 0.78rem !important;
  max-height: 260px !important; overflow-y: auto !important; border-radius: 6px !important;
}
.action-log * { font-family: 'JetBrains Mono', monospace !important; }

/* Ship cards transition */
.ship-card-wrap div {
  transition: border-color 0.5s ease, background 0.3s ease, box-shadow 0.3s ease !important;
}

/* Sidebar styling */
.sidebar-section {
  background: #262626 !important; border: 1px solid #404040 !important;
  padding: 12px !important; margin-bottom: 8px !important; border-radius: 8px !important;
}

/* Cinematic feed */
@keyframes cinematic-pulse { 0%,100%{opacity:1; text-shadow:0 0 10px rgba(238,76,44,0.6);} 50%{opacity:0.6; text-shadow:none;} }
@keyframes cinematic-slide { from{opacity:0;transform:translateY(10px)} to{opacity:1;transform:translateY(0)} }
.cinematic-entry { animation: cinematic-slide 0.4s ease-out; }
.cinematic-live { animation: cinematic-pulse 1.5s infinite; color: #EE4C2C !important; }
.cinematic-feed { max-height: 420px; overflow-y: auto; scroll-behavior: smooth; }

/* Manual control panel */
.manual-panel {
  background: linear-gradient(135deg, #262626, #1c1c1c) !important;
  border: 2px solid #404040 !important;
  padding: 20px !important; border-radius: 10px !important;
  margin-top: 16px !important;
}
.manual-panel:hover { border-color: #EE4C2C !important; }
.manual-execute-btn {
  background: linear-gradient(135deg, #2B7D6D, #1f5a4e) !important;
  border: none !important; color: #ffffff !important;
  font-weight: 700 !important; font-size: 1rem !important;
  padding: 10px 24px !important;
}
.manual-reset-btn {
  background: linear-gradient(135deg, #1c1c1c, #262626) !important;
  border: 1px solid #404040 !important; color: #0668E1 !important;
  font-weight: 600 !important; font-size: 1rem !important;
  padding: 10px 24px !important;
}
"""
TAB_OVERRIDE_CSS = """
/* Style the tab bar to highlight the Custom tab */
.tab-nav button[aria-selected="false"] { opacity: 0.6; }
.tab-nav button[aria-selected="true"] { border-bottom: 2px solid #0668E1 !important; }
"""

AUTO_SWITCH_JS = """
() => {
  document.body.classList.add('dark');
  var gc = document.querySelector('.gradio-container');
  if (gc) gc.classList.add('dark');

  /* Auto-scroll: watch for cinematic feed updates and scroll into view */
  var scrollObserver = new MutationObserver(function(mutations) {
    var feed = document.querySelector('.cinematic-feed');
    if (feed && feed.children.length > 0) {
      feed.scrollTop = feed.scrollHeight;
      feed.parentElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  });
  setTimeout(function() {
    var container = document.querySelector('.gradio-container');
    if (container) {
      scrollObserver.observe(container, { childList: true, subtree: true });
    }
  }, 1500);
}
"""

# ── Static HTML blocks ──────────────────────────────────────────────────

RUBRIC_HTML = """
<div style="background:#262626;border:1px solid #404040;padding:16px;border-radius:8px;font-size:0.82rem">
<table style="width:100%;border-collapse:collapse">
<tr style="border-bottom:1px solid #404040;color:#666666">
  <th style="padding:8px;text-align:left">Component</th>
  <th style="padding:8px;text-align:center">Weight</th>
  <th style="padding:8px;text-align:left">Formula</th></tr>
<tr style="border-bottom:1px solid #404040">
  <td style="padding:8px"><span style="color:#2B7D6D">\u25cf</span> Resolution Rate</td>
  <td style="padding:8px;text-align:center;font-weight:700">40%</td>
  <td style="padding:8px;color:#666666">resolved_exceptions / total</td></tr>
<tr style="border-bottom:1px solid #404040">
  <td style="padding:8px"><span style="color:#0668E1">\u25cf</span> Cost Efficiency</td>
  <td style="padding:8px;text-align:center;font-weight:700">25%</td>
  <td style="padding:8px;color:#666666">1 - (cost_spent / budget)</td></tr>
<tr style="border-bottom:1px solid #404040">
  <td style="padding:8px"><span style="color:#ffd740">\u25cf</span> SLA Compliance</td>
  <td style="padding:8px;text-align:center;font-weight:700">20%</td>
  <td style="padding:8px;color:#666666">1 - (violations / total)</td></tr>
<tr>
  <td style="padding:8px"><span style="color:#EE4C2C">\u25cf</span> Decision Quality</td>
  <td style="padding:8px;text-align:center;font-weight:700">15%</td>
  <td style="padding:8px;color:#666666">investigate-first + priority order</td></tr>
</table>
<div style="margin-top:12px;padding-top:12px;border-top:1px solid #404040;color:#666666;font-size:0.75rem">
<b style="color:#e0e6ed">Optimal 3-step sequence:</b> investigate ($50) \u2192 approve_refund ($1,500) \u2192 reschedule ($800) = 100% resolved<br>
<b style="color:#e0e6ed">Resolution actions:</b> reroute, reschedule, file_claim, approve_refund, split_shipment \u2014 only these can mark a shipment as resolved
</div>
</div>
"""

HOW_IT_WORKS_HTML = """
<div style="background:linear-gradient(135deg,#1c1c1c,#262626);border:1px solid #404040;
padding:20px;border-radius:8px;margin-bottom:16px">
<h2 style="margin:0 0 12px 0;font-size:1.1rem;color:#0668E1">\U0001f4e6 How MOGUL Logistics Works</h2>
<div style="font-size:0.85rem;line-height:1.6;color:#c8d6e0">
An <b>RL agent</b> resolves logistics shipment exceptions (delays, damages, misroutes, customs holds)
under <b>time pressure</b> (SLA deadlines) and <b>budget constraints</b>.<br><br>

<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:8px">
<div style="background:#26262680;padding:10px;border-radius:6px;border:1px solid #404040">
<div style="color:#2B7D6D;font-weight:700;font-size:0.78rem;margin-bottom:4px">\U0001f3af GOAL</div>
Resolve as many shipments as possible before SLA deadlines expire, while staying under budget.
</div>
<div style="background:#26262680;padding:10px;border-radius:6px;border:1px solid #404040">
<div style="color:#EE4C2C;font-weight:700;font-size:0.78rem;margin-bottom:4px">\u26a1 CHALLENGE</div>
Each step costs time \u2014 ALL active shipments' SLA deadlines tick down by 1 every step.
</div>
</div>

<div style="margin-top:12px;padding:10px;background:#26262680;border-radius:6px;border:1px solid #404040">
<div style="color:#ffd740;font-weight:700;font-size:0.78rem;margin-bottom:4px">\U0001f527 AGENT STRATEGY</div>
<code style="color:#0668E1">investigate</code> ($50) \u2192
<code style="color:#0668E1">approve_refund</code> ($1,500) \u2192
<code style="color:#0668E1">reschedule</code> ($800) = <span style="color:#2B7D6D;font-weight:700">100% resolved in 3 steps</span>
</div>
</div></div>
"""

INTRO_HTML = """
<div style="background:linear-gradient(135deg,#1c1c1c 0%,#262626 100%);
border:1px solid #404040;padding:20px 24px;margin-bottom:16px;border-radius:8px">
<div style="display:flex;justify-content:space-between;align-items:center">
<div>
<h1 style="margin:0;font-size:1.6rem;color:#e0e6ed;letter-spacing:-0.02em">MOGUL Logistics</h1>
<div style="color:#666666;font-size:0.82rem;margin-top:4px">
Shipment Exception Resolution \u2014 RL Environment</div>
</div>
<div style="text-align:right">
<div style="color:#0668E1;font-size:0.82rem;font-weight:600">OpenEnv Hackathon</div>
<div style="color:#666666;font-size:0.72rem">v1.0.0 \u00b7 Muhammed Sayeedur Rahman</div>
</div></div></div>
"""


# ── Render helpers ──────────────────────────────────────────────────────

def progress_bar(pct: float, width: int = 20) -> str:
    filled = int(pct * width)
    empty = width - filled
    colour = _GREEN if pct >= 1.0 else (_YELLOW if pct >= 0.5 else _BLUE)
    return (
        f'<span style="color:{colour}">{"█" * filled}</span>'
        f'<span style="color:#404040">{"░" * empty}</span>'
        f' {pct:.0%}'
    )


def sla_badge(steps: int) -> str:
    if steps <= 1:
        return f'<span style="color:{_RED};font-weight:700">\u26a0 SLA {steps}</span>'
    if steps <= 3:
        return f'<span style="color:{_YELLOW}">SLA {steps}</span>'
    return f'<span style="color:{_GREEN}">SLA {steps}</span>'


def status_colour(status: str) -> str:
    return {
        "resolved": _GREEN, "failed": _RED, "investigating": _BLUE,
        "action_taken": _ORANGE, "new": _MUTED,
    }.get(status, _MUTED)


def render_shipments(obs: dict) -> str:
    status_text = obs.get("shipment_status", "")
    progress_map = obs.get("resolution_progress", {})
    if not status_text or status_text == "No active shipments.":
        return (
            '<div style="text-align:center;padding:40px;color:#666666">'
            '<div style="font-size:2rem;margin-bottom:8px">\U0001f4e6</div>'
            'No active shipments \u2014 select a difficulty and click '
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

        col = status_colour(status_val)
        icon = _PRIO_ICON.get(priority, "")
        inv = (
            ' <span style="background:#1a3a5c;color:#0668E1;'
            'padding:1px 6px;font-size:0.6rem;border-radius:3px">\u2713 INVESTIGATED</span>'
            if status_val in ("investigating", "action_taken") else ""
        )
        resolved_glow = (
            "box-shadow:0 0 12px rgba(43,125,109,0.5);"
            if status_val == "resolved" else ""
        )
        failed_dim = "opacity:0.6;" if status_val == "failed" else ""

        cards.append(
            f'<div style="background:#262626;border:1px solid #404040;'
            f'border-left:3px solid {col};padding:10px 14px;margin-bottom:6px;'
            f'border-radius:4px;transition:all 0.3s ease;{resolved_glow}{failed_dim}">'
            f'<div style="display:flex;justify-content:space-between;align-items:center">'
            f'  <span style="font-weight:700;font-size:0.95rem">{sid}{inv}</span>'
            f'  <span style="font-size:0.72rem;color:{col};text-transform:uppercase;'
            f'font-weight:600">{status_val}</span></div>'
            f'<div style="font-size:0.78rem;color:#666666;margin:4px 0">'
            f'{icon} {priority} &middot; {exc_type}</div>'
            f'<div style="margin-top:6px">{progress_bar(prog)}</div>'
            f'<div style="text-align:right;margin-top:4px;font-size:0.72rem">'
            f'{sla_badge(sla_steps)}</div></div>'
        )
    return "\n".join(cards)


def render_stats(obs: dict) -> tuple[str, str, str, str]:
    pm = obs.get("resolution_progress", {})
    total = len(pm)
    resolved = sum(1 for v in pm.values() if v >= 1.0)
    budget = obs.get("budget_remaining", 0)
    time_left = obs.get("time_remaining", 0)
    failed = obs.get("shipment_status", "").count("status=failed")
    return (f"{resolved}/{total}", f"${budget:,.0f}", str(time_left), str(failed))


def render_scorecard(data: dict) -> str:
    obs = data.get("observation", {})
    reward = data.get("reward", 0.0)
    if not data.get("done"):
        return ""

    pm = obs.get("resolution_progress", {})
    total = max(len(pm), 1)
    resolved = sum(1 for v in pm.values() if v >= 1.0)
    score = reward or 0.0
    score_col = _GREEN if score >= 0.8 else (_YELLOW if score >= 0.6 else _RED)

    res_s = (resolved / total) * 0.4

    def _bar(val: float, mx: float, col: str, label: str) -> str:
        pct = min(val / max(mx, 0.001), 1.0) * 100
        return (
            f'<div style="margin:8px 0">'
            f'<div style="display:flex;justify-content:space-between;font-size:0.78rem">'
            f'<span>{label}</span><span style="color:{col}">{val:.4f}</span></div>'
            f'<div style="background:#404040;height:12px;border-radius:6px;overflow:hidden">'
            f'<div style="background:{col};height:100%;width:{pct:.1f}%;'
            f'border-radius:6px;transition:width 0.5s ease"></div></div></div>'
        )

    bars = (
        _bar(res_s, 0.40, _GREEN, f"Resolution Rate ({resolved}/{total})")
        + _bar(min(0.25, max(0, score - res_s)), 0.25, _BLUE, "Cost Efficiency")
        + _bar(0.20, 0.20, _YELLOW, "SLA Compliance")
        + _bar(max(0, score - res_s - 0.25 - 0.20), 0.15, _ORANGE, "Decision Quality")
    )

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
        sc = status_colour(st)
        rows += (
            f'<tr style="border-bottom:1px solid #404040">'
            f'<td style="padding:6px 8px">{sid}</td>'
            f'<td style="padding:6px 8px;color:{sc};font-weight:600">{st.upper()}</td>'
            f'<td style="padding:6px 8px">{p:.0%}</td></tr>'
        )

    return (
        f'<div style="background:linear-gradient(135deg,#0d2137,#262626);'
        f'border:2px solid {score_col};padding:24px;margin-top:16px;border-radius:12px;'
        f'box-shadow:0 0 20px rgba(0,0,0,0.5)">'
        f'<div style="text-align:center;margin-bottom:20px">'
        f'<div style="font-size:0.7rem;color:#666666;text-transform:uppercase;'
        f'letter-spacing:0.15em;margin-bottom:4px">FINAL SCORE</div>'
        f'<div style="font-size:3.5rem;font-weight:800;color:{score_col};'
        f'text-shadow:0 0 20px {score_col}40">{score:.4f}</div></div>'
        f'<div style="max-width:500px;margin:0 auto">{bars}</div>'
        f'<div style="margin-top:20px">'
        f'<div style="font-size:0.7rem;color:#666666;text-transform:uppercase;'
        f'letter-spacing:0.1em;margin-bottom:8px">SHIPMENT OUTCOMES</div>'
        f'<table style="width:100%;font-size:0.82rem;border-collapse:collapse">'
        f'<tr style="color:#666666;border-bottom:1px solid #404040">'
        f'<th style="padding:6px 8px;text-align:left">ID</th>'
        f'<th style="padding:6px 8px;text-align:left">Status</th>'
        f'<th style="padding:6px 8px;text-align:left">Progress</th></tr>'
        f'{rows}</table></div></div>'
    )


def render_cinematic_feed(events: list[dict], is_live: bool = False) -> str:
    """Render a cinematic timeline of agent actions."""
    if not events:
        return ""

    live_badge = (
        '<span class="cinematic-live" style="background:#EE4C2C;color:white;'
        'padding:2px 10px;border-radius:4px;font-size:0.65rem;font-weight:700;'
        'margin-left:10px">\u25cf LIVE</span>'
        if is_live else
        '<span style="background:#2B7D6D;color:#0f1923;padding:2px 10px;'
        'border-radius:4px;font-size:0.65rem;font-weight:700;'
        'margin-left:10px">\u2713 COMPLETE</span>'
    )

    entries_html = ""
    for i, ev in enumerate(events):
        is_latest = (i == len(events) - 1)
        icon = ACTION_ICONS.get(ev["action"], "\u26a1")
        color = ACTION_COLORS.get(ev["action"], "#0668E1")
        cost = int(ACTION_COSTS.get(ev["action"], 0))

        glow = f"box-shadow:0 0 15px {color}30;" if is_latest else ""
        border_c = color if is_latest else "#404040"
        bg = "#1c1c1c" if not is_latest else "#262626"

        cost_html = (
            f'<span style="color:#ffd740;font-weight:600;font-size:0.82rem">'
            f'${cost:,}</span>'
            if ev["action"] != "reset" else ""
        )
        step_label = (
            f'<span style="color:{color};font-weight:700;font-size:0.88rem">'
            f'STEP {ev["step"]}</span>'
            if ev["step"] > 0 else
            f'<span style="color:{color};font-weight:700;font-size:0.88rem">'
            f'START</span>'
        )

        entry = (
            f'<div class="cinematic-entry" style="background:{bg};'
            f'border:1px solid {border_c};border-left:3px solid {color};'
            f'border-radius:6px;padding:12px 16px;margin-bottom:8px;{glow}'
            f'transition:all 0.3s ease">'
            f'<div style="display:flex;justify-content:space-between;align-items:center">'
            f'<div style="display:flex;align-items:center;gap:10px">'
            f'<span style="font-size:1.3rem">{icon}</span>'
            f'{step_label}'
            f'<span style="color:#e0e6ed;font-weight:600;font-size:0.88rem">'
            f'{ev["action"].replace("_"," ").upper()}</span>'
            f'<span style="color:#666666;font-size:0.78rem">\u2192 {ev["target"]}</span>'
            f'</div>'
            f'{cost_html}</div>'
            f'<div style="color:#c8d6e0;font-size:0.82rem;margin-top:8px;'
            f'padding-left:36px;line-height:1.5">'
            f'\U0001f4ad {ev["explanation"]}</div>'
        )

        if ev.get("done") and ev.get("reward") is not None:
            r = ev["reward"]
            sc = _GREEN if r >= 0.7 else (_YELLOW if r >= 0.5 else _RED)
            entry += (
                f'<div style="margin-top:10px;padding:10px 16px;'
                f'background:linear-gradient(135deg,#262626,#1a3a5c);'
                f'border-radius:6px;text-align:center;border:1px solid {sc}">'
                f'<span style="font-size:0.72rem;color:#666666;'
                f'text-transform:uppercase;letter-spacing:0.1em">'
                f'EPISODE COMPLETE \u2014 FINAL SCORE </span>'
                f'<span style="color:{sc};font-weight:800;font-size:1.4rem;'
                f'text-shadow:0 0 12px {sc}40">{r:.4f}</span></div>'
            )

        entry += '</div>'
        entries_html += entry

    return (
        f'<div style="background:linear-gradient(135deg,#0d2137,#262626);'
        f'border:1px solid #404040;border-radius:10px;padding:16px;margin:12px 0">'
        f'<div style="display:flex;align-items:center;margin-bottom:14px">'
        f'<span style="font-size:0.82rem;color:#666666;text-transform:uppercase;'
        f'letter-spacing:0.12em;font-weight:600">\U0001f3ac Agent Activity Feed</span>'
        f'{live_badge}</div>'
        f'<div class="cinematic-feed">{entries_html}</div></div>'
    )
