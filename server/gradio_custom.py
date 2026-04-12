"""MOGUL Logistics — Gradio dashboard (judge-ready).

Clean, focused layout. No manual control panel, no route map, no
constraint monitor. Just the signal that matters:

  1. What is this environment? (intro + how it works)
  2. Run the agent on 3 difficulty tiers.
  3. Watch shipments get resolved + read the agent's reasoning live.
  4. See the final composite score with per-component breakdown.
  5. Compare trained policy vs heuristic vs random baselines.
  6. Read the grading rubric.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any, Dict, List, Optional

import gradio as gr

from .constants import ACTION_COSTS
from .gradio_styles import (
    AUTO_SWITCH_JS,
    CUSTOM_CSS,
    HOW_IT_WORKS_HTML,
    INTRO_HTML,
    RUBRIC_HTML,
    TASK_INFO,
    render_cinematic_feed,
    render_scorecard,
    render_shipments,
    render_stats,
    render_training_results,
)
from .heuristic import HeuristicPlanner


def build_custom_dashboard(
    web_manager: Any,
    action_fields: List[Dict[str, Any]],
    metadata: Any,
    is_chat_env: bool,
    title: str,
    quick_start_md: Optional[str],
) -> gr.Blocks:
    """Build the MOGUL Logistics judge-ready dashboard."""

    cinematic_events: list[dict] = []
    step_counter: list[int] = [0]

    # ── helpers ──────────────────────────────────────────────────────────

    def _task_id(label: str) -> str:
        return TASK_INFO.get(label, "task_easy")

    def _wrap_feedback(text: str) -> str:
        return (
            f'<div style="background:#0c0d0f;border:1px solid rgba(255,255,255,.08);'
            f'padding:11px 14px;border-radius:8px;font-family:\'DM Mono\',monospace;'
            f'font-size:.76rem;color:#e0e6ed;white-space:pre-wrap;line-height:1.6">'
            f'{text}</div>'
        )

    # ── reset ────────────────────────────────────────────────────────────

    async def do_reset(task_label: str):
        cinematic_events.clear()
        step_counter[0] = 0

        data = await web_manager.reset_environment(
            reset_kwargs={"task_id": _task_id(task_label)},
        )
        obs = data.get("observation", {})

        # Seed the feed with an opening "reset" event so it never looks empty
        cinematic_events.append({
            "step":        0,
            "action":      "reset",
            "target":      _task_id(task_label),
            "explanation": "Episode initialized. Agent is reading shipment state.",
            "reward":      None,
            "done":        False,
        })

        return (
            render_shipments(obs),
            *render_stats(obs),
            _wrap_feedback(obs.get("feedback", "Episode started.")),
            render_cinematic_feed(cinematic_events, is_live=False),
            json.dumps(data, indent=2),
            "",
        )

    # ── auto demo (runs heuristic agent through the episode) ────────────

    async def do_auto_run(task_label: str, speed: float):
        cinematic_events.clear()
        step_counter[0] = 0
        planner = HeuristicPlanner()

        data = await web_manager.reset_environment(
            reset_kwargs={"task_id": _task_id(task_label)},
        )
        obs  = data.get("observation", {})
        done = data.get("done", False)

        cinematic_events.append({
            "step":        0,
            "action":      "reset",
            "target":      _task_id(task_label),
            "explanation": "Episode initialized. Agent is reading shipment state.",
            "reward":      None,
            "done":        False,
        })

        yield (
            render_shipments(obs),
            *render_stats(obs),
            _wrap_feedback(obs.get("feedback", "Episode started.")),
            render_cinematic_feed(cinematic_events, is_live=True),
            json.dumps(data, indent=2),
            "",
        )

        while not done:
            await asyncio.sleep(max(0.2, min(3.0, speed)))
            action, explanation = planner.pick_action(obs)

            data = await web_manager.step_environment({
                "action_type":        action["action_type"],
                "target_shipment_id": action["target_shipment_id"],
                "parameters":         action.get("parameters", {}),
            })
            obs    = data.get("observation", {})
            reward = data.get("reward")
            done   = data.get("done", False)

            step_counter[0] += 1

            cinematic_events.append({
                "step":        step_counter[0],
                "action":      action["action_type"],
                "target":      action["target_shipment_id"],
                "explanation": explanation,
                "reward":      reward,
                "done":        done,
            })

            scorecard = render_scorecard(data) if done else ""

            yield (
                render_shipments(obs, last_acted_on=action["target_shipment_id"]),
                *render_stats(obs),
                _wrap_feedback(obs.get("feedback", "")),
                render_cinematic_feed(cinematic_events, is_live=not done),
                json.dumps(data, indent=2),
                scorecard,
            )

    # ── run all difficulties (benchmark mode) ───────────────────────────

    async def do_run_all(_speed: float):
        results: dict[str, float] = {}
        for label, tid in TASK_INFO.items():
            planner = HeuristicPlanner()
            data    = await web_manager.reset_environment(reset_kwargs={"task_id": tid})
            obs     = data.get("observation", {})
            done    = data.get("done", False)
            while not done:
                await asyncio.sleep(0.03)
                action, _ = planner.pick_action(obs)
                data  = await web_manager.step_environment({
                    "action_type":        action["action_type"],
                    "target_shipment_id": action["target_shipment_id"],
                    "parameters":         action.get("parameters", {}),
                })
                obs  = data.get("observation", {})
                done = data.get("done", False)
            results[label] = data.get("reward", 0.0)

        rows = ""
        for label, sc in results.items():
            col = "#22c55e" if sc >= .7 else ("#f59e0b" if sc >= .5 else "#ef4444")
            short = label.split("—")[0].strip()
            rows += (
                f'<div style="margin:10px 0">'
                f'<div style="display:flex;justify-content:space-between;font-size:.82rem;margin-bottom:4px">'
                f'<span style="font-weight:600">{short}</span>'
                f'<span style="color:{col};font-weight:700;font-family:\'DM Mono\',monospace">{sc:.4f}</span></div>'
                f'<div style="background:rgba(255,255,255,.06);height:12px;border-radius:6px;overflow:hidden">'
                f'<div style="background:{col};height:100%;width:{sc*100:.1f}%;border-radius:6px;'
                f'transition:width .5s ease"></div></div></div>'
            )

        avg     = sum(results.values()) / max(len(results), 1)
        avg_col = "#22c55e" if avg >= .7 else ("#f59e0b" if avg >= .5 else "#ef4444")

        return (
            f'<div style="background:#13151a;border:1px solid {avg_col}40;'
            f'border-radius:12px;padding:22px;margin-top:14px">'
            f'<div style="text-align:center;margin-bottom:16px">'
            f'<div style="font-size:.6rem;color:#6b7280;text-transform:uppercase;'
            f'letter-spacing:.12em;margin-bottom:4px">Heuristic Agent · All Tiers Average</div>'
            f'<div style="font-size:2.8rem;font-weight:700;color:{avg_col};'
            f'letter-spacing:-.04em">{avg:.4f}</div></div>'
            f'{rows}</div>'
        )

    # ── Layout ───────────────────────────────────────────────────────────

    with gr.Blocks() as dashboard:
        # Inject CSS via a hidden HTML element (Gradio 6.0+ removed the css=
        # kwarg from Blocks — it now belongs on launch() which OpenEnv
        # manages for us. This keeps the same styling without the warning).
        gr.HTML(f"<style>{CUSTOM_CSS}</style>")

        with gr.Column(elem_classes="mogul-root"):

            gr.HTML(INTRO_HTML)
            gr.HTML(HOW_IT_WORKS_HTML)

            # ── Difficulty buttons ──
            gr.HTML(
                '<div style="font-size:.6rem;font-weight:700;letter-spacing:.1em;'
                'text-transform:uppercase;color:#6b7280;margin:10px 0 6px">Difficulty</div>'
            )
            with gr.Row(elem_classes="diff-row"):
                btn_easy = gr.Button(
                    "Easy\n1 ship · 5 steps · $5K",
                    elem_classes="diff-btn diff-easy",
                )
                btn_med = gr.Button(
                    "Medium\n4 ships · 10 steps · $12K",
                    elem_classes="diff-btn diff-med",
                )
                btn_hard = gr.Button(
                    "Hard\n8 ships · 15 steps · $15K",
                    elem_classes="diff-btn diff-hard",
                )

            # Hidden state to track selected difficulty
            task_selector = gr.State(list(TASK_INFO.keys())[0])

            # ── Demo controls ──
            with gr.Row(elem_classes="demo-controls"):
                speed_slider = gr.Slider(
                    minimum=0.3, maximum=2.0, value=0.6, step=0.1,
                    label="Demo speed (sec / step)",
                    scale=3,
                )
                demo_btn = gr.Button(
                    "Run Agent Demo",
                    variant="primary",
                    elem_classes="btn-demo",
                    scale=2,
                )
                run_all_btn = gr.Button(
                    "Benchmark all tiers",
                    variant="secondary",
                    elem_classes="btn-demo-all",
                    scale=2,
                )

            # ── Stat cards ──
            with gr.Row():
                stat_resolved = gr.Textbox(
                    value="0/0", label="RESOLVED", interactive=False,
                    elem_classes="stat-card",
                )
                stat_budget = gr.Textbox(
                    value="$0", label="BUDGET LEFT", interactive=False,
                    elem_classes="stat-card",
                )
                stat_time = gr.Textbox(
                    value="0", label="STEPS LEFT", interactive=False,
                    elem_classes="stat-card",
                )
                stat_sla = gr.Textbox(
                    value="0", label="FAILED", interactive=False,
                    elem_classes="stat-card",
                )

            # ── Shipments + Agent Feed side by side ──
            with gr.Row():
                with gr.Column(scale=3):
                    gr.HTML(
                        '<div style="font-size:.6rem;font-weight:700;letter-spacing:.1em;'
                        'text-transform:uppercase;color:#6b7280;margin:10px 0 6px">Shipments</div>'
                    )
                    shipments_display = gr.HTML(
                        value=(
                            '<div style="text-align:center;padding:44px;color:#4b5563;min-height:160px">'
                            '<div style="font-size:1.8rem;margin-bottom:8px;opacity:.4">📦</div>'
                            '<div style="font-size:.82rem">Select difficulty → Run Agent Demo</div>'
                            '</div>'
                        )
                    )
                    gr.HTML(
                        '<div style="font-size:.6rem;font-weight:700;letter-spacing:.1em;'
                        'text-transform:uppercase;color:#6b7280;margin:14px 0 6px">Last Feedback</div>'
                    )
                    feedback_display = gr.HTML(
                        value=(
                            '<div style="background:#0c0d0f;border:1px solid rgba(255,255,255,.08);'
                            'padding:11px 14px;border-radius:8px;font-family:DM Mono,monospace;'
                            'font-size:.76rem;color:#3b82f6">Ready — click Run Agent Demo.</div>'
                        )
                    )

                with gr.Column(scale=2):
                    gr.HTML(
                        '<div style="font-size:.6rem;font-weight:700;letter-spacing:.1em;'
                        'text-transform:uppercase;color:#6b7280;margin:10px 0 6px">Agent Activity</div>'
                    )
                    feed_display = gr.HTML(value=render_cinematic_feed([], is_live=False))

            # ── Final scorecard (appears after episode ends) ──
            scorecard_display = gr.HTML(value="")

            # ── Benchmark comparison (Run All) ──
            comparison_display = gr.HTML(value="")

            # ── RL Training Results (centerpiece) ──
            gr.HTML(
                '<div style="font-size:.6rem;font-weight:700;letter-spacing:.1em;'
                'text-transform:uppercase;color:#6b7280;margin:22px 0 10px">'
                'RL Training Results</div>'
            )
            gr.HTML(render_training_results())

            # ── Grading Rubric (collapsible, secondary) ──
            with gr.Accordion("Grading Rubric — Composite Reward Function", open=False):
                gr.HTML(RUBRIC_HTML)

            # ── Raw JSON for debugging (collapsed) ──
            with gr.Accordion("Raw JSON Response (for debugging)", open=False):
                raw_json = gr.Code(value="", language="json", interactive=False)

        # ── Shared output list ──
        _outputs = [
            shipments_display,
            stat_resolved, stat_budget, stat_time, stat_sla,
            feedback_display,
            feed_display,
            raw_json,
            scorecard_display,
        ]

        # ── Wiring ──

        _diff_keys = list(TASK_INFO.keys())

        async def _select_easy():
            return [_diff_keys[0]] + list(await do_reset(_diff_keys[0]))

        async def _select_med():
            return [_diff_keys[1]] + list(await do_reset(_diff_keys[1]))

        async def _select_hard():
            return [_diff_keys[2]] + list(await do_reset(_diff_keys[2]))

        _sel_outputs = [task_selector] + _outputs

        btn_easy.click(fn=_select_easy, inputs=[], outputs=_sel_outputs)
        btn_med.click(fn=_select_med, inputs=[], outputs=_sel_outputs)
        btn_hard.click(fn=_select_hard, inputs=[], outputs=_sel_outputs)

        async def _demo_wrap(task_label, speed):
            async for r in do_auto_run(task_label, speed):
                yield list(r)

        demo_btn.click(
            fn=_demo_wrap,
            inputs=[task_selector, speed_slider],
            outputs=_outputs,
        )
        run_all_btn.click(
            fn=do_run_all,
            inputs=[speed_slider],
            outputs=[comparison_display],
        )

        dashboard.load(fn=None, js=AUTO_SWITCH_JS)

    return dashboard
