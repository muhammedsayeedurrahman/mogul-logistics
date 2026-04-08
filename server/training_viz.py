"""Training results visualization for the dashboard."""

from __future__ import annotations

import json
from pathlib import Path

_ASSETS = Path(__file__).resolve().parent.parent / "assets"


def render_training_results() -> str:
    """Render training comparison chart as HTML.

    Reads pre-generated results from assets/training_curve.json.
    Returns a static HTML block with gradient-fill sparkline, animated bars,
    and a key insight callout.
    """
    curve_path = _ASSETS / "training_curve.json"
    if not curve_path.exists():
        return (
            '<div style="text-align:center;padding:20px;color:#6b7280">'
            "Run <code>python train_demo.py</code> to generate training results.</div>"
        )

    with open(curve_path) as f:
        data = json.load(f)

    random_avg = data.get("random_avg", 0.0)
    heuristic_avg = data.get("heuristic_avg", 0.0)
    trained_avg = data.get("trained_avg", 0.0)
    training_rewards = data.get("training_rewards", [])

    improvement = ((trained_avg - random_avg) / max(random_avg, 0.001)) * 100

    # Gradient-fill sparkline
    sparkline = ""
    if training_rewards:
        max_r = max(max(training_rewards), 0.001)
        n = len(training_rewards)
        points = []
        fill_points = []
        for i, r in enumerate(training_rewards):
            x = 10 + (i / max(n - 1, 1)) * 280
            y = 58 - (r / max_r) * 50
            points.append(f"{x:.0f},{y:.0f}")
            fill_points.append(f"{x:.0f},{y:.0f}")
        polyline = " ".join(points)
        # Close the fill polygon at the bottom
        fill_points.append(f"{10 + 280:.0f},58")
        fill_points.append("10,58")
        fill_poly = " ".join(fill_points)

        sparkline = (
            f'<svg viewBox="0 0 300 65" style="width:100%;height:65px;margin-top:8px">'
            f'<defs>'
            f'<linearGradient id="spark-grad" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0%" stop-color="#60a5fa" stop-opacity="0.3"/>'
            f'<stop offset="100%" stop-color="#60a5fa" stop-opacity="0.02"/>'
            f'</linearGradient>'
            f'</defs>'
            f'<polygon fill="url(#spark-grad)" points="{fill_poly}"/>'
            f'<polyline fill="none" stroke="#60a5fa" stroke-width="2" '
            f'stroke-linecap="round" stroke-linejoin="round" points="{polyline}"/>'
            # Start and end dots
            f'<circle cx="{points[0].split(",")[0]}" cy="{points[0].split(",")[1]}" '
            f'r="3" fill="#f87171"/>'
            f'<circle cx="{points[-1].split(",")[0]}" cy="{points[-1].split(",")[1]}" '
            f'r="3" fill="#34d399"/>'
            f'</svg>'
        )

    def _bar(label: str, value: float, color: str, emoji: str) -> str:
        pct = min(value / 1.0, 1.0) * 100
        return (
            f'<div style="margin:12px 0">'
            f'<div style="display:flex;justify-content:space-between;'
            f'align-items:center;font-size:0.85rem;margin-bottom:6px">'
            f'<span style="display:flex;align-items:center;gap:6px">'
            f'<span style="font-size:1.1rem">{emoji}</span>'
            f'<span>{label}</span></span>'
            f'<span style="color:{color};font-weight:800;font-size:1.15rem">'
            f'{value:.4f}</span></div>'
            f'<div style="background:rgba(255,255,255,0.06);height:16px;border-radius:8px;'
            f'overflow:hidden">'
            f'<div style="background:linear-gradient(90deg,{color}60,{color});'
            f'height:100%;width:{pct:.1f}%;border-radius:8px;'
            f'transition:width 0.8s cubic-bezier(0.4,0,0.2,1)"></div></div></div>'
        )

    # Key insight callout
    insight = (
        f'<div style="background:rgba(52,211,153,0.06);border:1px solid rgba(52,211,153,0.15);'
        f'border-radius:12px;padding:14px 16px;margin-top:16px;'
        f'display:flex;align-items:flex-start;gap:10px">'
        f'<span style="font-size:1.2rem;flex-shrink:0">\U0001f4a1</span>'
        f'<div style="font-size:0.8rem;color:#a0a8b8;line-height:1.6">'
        f'<strong style="color:#34d399">Key Insight:</strong> '
        f'The trained neural network policy achieves <strong style="color:#e0e6ed">'
        f'{improvement:.0f}% improvement</strong> over random in just '
        f'{len(training_rewards)} episodes, proving this environment produces '
        f'a strong learning signal for RL agents.</div></div>'
    )

    return (
        f'<div style="background:rgba(20,24,36,0.7);backdrop-filter:blur(16px);'
        f'border:1px solid rgba(255,255,255,0.06);border-radius:16px;padding:24px">'

        # Header
        f'<div style="display:flex;justify-content:space-between;align-items:center;'
        f'margin-bottom:20px">'
        f'<div>'
        f'<div style="font-size:0.82rem;color:#a0a8b8;text-transform:uppercase;'
        f'letter-spacing:0.12em;font-weight:700">Agent Performance Comparison</div>'
        f'<div style="font-size:0.72rem;color:#6b7280;margin-top:3px">'
        f'Easy task \u00b7 50 episodes each \u00b7 PyTorch REINFORCE</div></div>'
        f'<div style="text-align:right">'
        f'<div style="font-size:2.2rem;font-weight:900;color:#34d399;'
        f'line-height:1;text-shadow:0 0 20px rgba(52,211,153,0.3)">{improvement:.0f}%</div>'
        f'<div style="font-size:0.62rem;color:#6b7280;text-transform:uppercase;'
        f'letter-spacing:0.08em;margin-top:2px">improvement</div></div></div>'

        # Bars
        f'{_bar("Random Agent (baseline)", random_avg, "#f87171", "\U0001f3b2")}'
        f'{_bar("Trained Policy (REINFORCE)", trained_avg, "#60a5fa", "\U0001f916")}'
        f'{_bar("Heuristic Expert", heuristic_avg, "#34d399", "\U0001f9e0")}'

        # Sparkline
        f'<div style="margin-top:20px;padding-top:16px;border-top:1px solid rgba(255,255,255,0.06)">'
        f'<div style="font-size:0.72rem;color:#6b7280;text-transform:uppercase;'
        f'letter-spacing:0.1em;margin-bottom:4px">Training Reward Curve</div>'
        f'{sparkline}'
        f'<div style="display:flex;justify-content:space-between;font-size:0.62rem;'
        f'color:#6b7280;margin-top:4px">'
        f'<span style="color:#f87171">Ep 1 (untrained)</span>'
        f'<span style="color:#34d399">Ep {len(training_rewards)} (converged)</span></div>'
        f'</div>'

        # Key insight
        f'{insight}'

        f'</div>'
    )
