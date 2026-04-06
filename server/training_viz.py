"""Training results visualization for the dashboard."""

from __future__ import annotations

import json
from pathlib import Path

_ASSETS = Path(__file__).resolve().parent.parent / "assets"

_GREEN = "#00e676"
_RED = "#ff5252"
_BLUE = "#40c4ff"
_YELLOW = "#ffd740"
_ORANGE = "#ff9100"


def render_training_results() -> str:
    """Render training comparison chart as HTML.

    Reads pre-generated results from assets/training_curve.json.
    Returns a static HTML block showing random vs heuristic/trained comparison.
    """
    curve_path = _ASSETS / "training_curve.json"
    if not curve_path.exists():
        return (
            '<div style="text-align:center;padding:20px;color:#7a8ea0">'
            "Run <code>python train_demo.py</code> to generate training results.</div>"
        )

    with open(curve_path) as f:
        data = json.load(f)

    random_avg = data.get("random_avg", 0.0)
    heuristic_avg = data.get("heuristic_avg", 0.0)
    trained_avg = data.get("trained_avg", 0.0)
    training_rewards = data.get("training_rewards", [])

    # Compute improvement
    improvement = ((trained_avg - random_avg) / max(random_avg, 0.001)) * 100

    # Mini sparkline from training rewards
    sparkline = ""
    if training_rewards:
        max_r = max(max(training_rewards), 0.001)
        n = len(training_rewards)
        points = []
        for i, r in enumerate(training_rewards):
            x = (i / max(n - 1, 1)) * 280
            y = 55 - (r / max_r) * 50
            points.append(f"{x:.0f},{y:.0f}")
        polyline = " ".join(points)
        sparkline = (
            f'<svg viewBox="0 0 280 60" style="width:100%;height:60px;margin-top:8px">'
            f'<polyline fill="none" stroke="{_BLUE}" stroke-width="1.5" '
            f'points="{polyline}"/>'
            f'</svg>'
        )

    def _bar(label: str, value: float, color: str, emoji: str) -> str:
        pct = min(value / 1.0, 1.0) * 100
        return (
            f'<div style="margin:10px 0">'
            f'<div style="display:flex;justify-content:space-between;'
            f'align-items:center;font-size:0.85rem;margin-bottom:4px">'
            f'<span>{emoji} {label}</span>'
            f'<span style="color:{color};font-weight:700;font-size:1.1rem">'
            f'{value:.4f}</span></div>'
            f'<div style="background:#1e3a5f;height:20px;border-radius:10px;'
            f'overflow:hidden">'
            f'<div style="background:linear-gradient(90deg,{color}80,{color});'
            f'height:100%;width:{pct:.1f}%;border-radius:10px;'
            f'transition:width 0.5s ease"></div></div></div>'
        )

    return (
        f'<div style="background:linear-gradient(135deg,#0d2137,#162332);'
        f'border:1px solid #1e3a5f;border-radius:10px;padding:20px">'
        f'<div style="display:flex;justify-content:space-between;align-items:center;'
        f'margin-bottom:16px">'
        f'<div>'
        f'<div style="font-size:0.82rem;color:#7a8ea0;text-transform:uppercase;'
        f'letter-spacing:0.12em;font-weight:600">Agent Performance Comparison</div>'
        f'<div style="font-size:0.72rem;color:#7a8ea0;margin-top:2px">'
        f'Easy task \u00b7 50 episodes each</div></div>'
        f'<div style="text-align:right">'
        f'<div style="font-size:2rem;font-weight:800;color:{_GREEN};'
        f'line-height:1">{improvement:.0f}%</div>'
        f'<div style="font-size:0.65rem;color:#7a8ea0;text-transform:uppercase;'
        f'letter-spacing:0.05em">improvement</div></div></div>'
        f'{_bar("Random Agent (baseline)", random_avg, _RED, "\U0001f3b2")}'
        f'{_bar("Heuristic Agent", heuristic_avg, _GREEN, "\U0001f9e0")}'
        f'{_bar("Trained Policy", trained_avg, _BLUE, "\U0001f916")}'
        f'<div style="margin-top:16px;padding-top:12px;border-top:1px solid #1e3a5f">'
        f'<div style="font-size:0.72rem;color:#7a8ea0;text-transform:uppercase;'
        f'letter-spacing:0.1em;margin-bottom:4px">Training Reward Curve</div>'
        f'{sparkline}'
        f'<div style="display:flex;justify-content:space-between;font-size:0.65rem;'
        f'color:#7a8ea0;margin-top:2px">'
        f'<span>Episode 1</span><span>Episode {len(training_rewards)}</span></div>'
        f'</div></div>'
    )
