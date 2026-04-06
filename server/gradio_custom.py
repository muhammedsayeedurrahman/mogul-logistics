"""Custom Gradio dashboard for MOGUL Logistics environment.

Judge-friendly dashboard with sidebar controls, auto-run demo,
real-time reward chart, scorecard, and grading rubric.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any, Dict, List, Optional

import gradio as gr

from .constants import ACTION_COSTS
from .gradio_styles import (
    ACTION_COLORS,
    ACTION_ICONS,
    AUTO_SWITCH_JS,
    CUSTOM_CSS,
    HOW_IT_WORKS_HTML,
    INTRO_HTML,
    RUBRIC_HTML,
    TAB_OVERRIDE_CSS,
    TASK_INFO,
    render_cinematic_feed,
    render_scorecard,
    render_shipments,
    render_stats,
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
        data = await web_manager.reset_environment(
            reset_kwargs={"task_id": tid},
        )
        obs = data.get("observation", {})
        return (
            render_shipments(obs),
            *render_stats(obs),
            _wrap(obs.get("feedback", "Episode started.")),
            "",
            json.dumps(data, indent=2),
            "",
            "",
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
            entry += "  \u2713 DONE"
        action_log_entries.append(entry)

        scorecard = render_scorecard(data) if done else ""

        icon = ACTION_ICONS.get(action_type, "\u26a1")
        color = ACTION_COLORS.get(action_type, "#40c4ff")
        manual_narration = (
            f'<div style="background:linear-gradient(135deg,#0d2137,#162332);'
            f'border:1px solid #1e3a5f;border-radius:10px;padding:16px;margin:12px 0">'
            f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:10px">'
            f'<span style="font-size:0.82rem;color:#7a8ea0;text-transform:uppercase;'
            f'letter-spacing:0.12em;font-weight:600">\U0001f3ae Manual Action</span></div>'
            f'<div class="cinematic-entry" style="background:#0d1520;'
            f'border:1px solid {color};border-left:3px solid {color};'
            f'border-radius:6px;padding:12px 16px;box-shadow:0 0 15px {color}30">'
            f'<div style="display:flex;justify-content:space-between;align-items:center">'
            f'<div style="display:flex;align-items:center;gap:10px">'
            f'<span style="font-size:1.3rem">{icon}</span>'
            f'<span style="color:{color};font-weight:700;font-size:0.88rem">'
            f'STEP {step_counter[0]}</span>'
            f'<span style="color:#e0e6ed;font-weight:600">'
            f'{action_type.replace("_"," ").upper()}</span>'
            f'<span style="color:#7a8ea0;font-size:0.78rem">\u2192 {target_id}</span>'
            f'</div>'
            f'<span style="color:#ffd740;font-weight:600">${cost:,}</span></div>'
            f'<div style="color:#c8d6e0;font-size:0.82rem;margin-top:8px;'
            f'padding-left:36px">\U0001f4ad Manual action executed by user</div>'
            f'</div></div>'
        )

        return (
            render_shipments(obs),
            *render_stats(obs),
            _wrap(obs.get("feedback", "")),
            "\n".join(action_log_entries),
            json.dumps(data, indent=2),
            scorecard,
            manual_narration,
        )

    async def do_auto_run(task_label, speed):
        """Step-by-step auto-run with cinematic narration."""
        action_log_entries.clear()
        reward_history.clear()
        step_counter[0] = 0
        tid = _task_id(task_label)
        cinematic_events: list[dict] = []
        planner = HeuristicPlanner()

        data = await web_manager.reset_environment(
            reset_kwargs={"task_id": tid},
        )
        obs = data.get("observation", {})

        cinematic_events.append({
            "step": 0, "action": "reset", "target": tid,
            "explanation": (
                f"Episode initialized \u2014 {task_label}. "
                "Agent scanning shipments and planning optimal "
                "resolution order..."
            ),
            "reward": None, "done": False,
        })
        yield (
            render_shipments(obs),
            *render_stats(obs),
            _wrap(obs.get("feedback", "Episode started.")),
            "",
            json.dumps(data, indent=2),
            "",
            render_cinematic_feed(cinematic_events, is_live=True),
        )

        done = data.get("done", False)
        while not done:
            delay = max(0.2, min(3.0, speed))
            await asyncio.sleep(delay)

            action, explanation = planner.pick_action(obs)
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
                entry += "  \u2713 DONE"
            action_log_entries.append(entry)
            scorecard = render_scorecard(data) if done else ""

            cinematic_events.append({
                "step": step_counter[0],
                "action": action["action_type"],
                "target": action["target_shipment_id"],
                "explanation": explanation,
                "reward": reward if done else None,
                "done": done,
            })

            yield (
                render_shipments(obs),
                *render_stats(obs),
                _wrap(obs.get("feedback", "")),
                "\n".join(action_log_entries),
                json.dumps(data, indent=2),
                scorecard,
                render_cinematic_feed(cinematic_events, is_live=not done),
            )

    async def do_run_all(speed):
        """Run all 3 difficulties sequentially and show comparison."""
        results = {}
        for label, tid in TASK_INFO.items():
            action_log_entries.clear()
            step_counter[0] = 0
            planner = HeuristicPlanner()

            data = await web_manager.reset_environment(
                reset_kwargs={"task_id": tid},
            )
            obs = data.get("observation", {})
            done = data.get("done", False)

            while not done:
                await asyncio.sleep(0.05)
                action, _ = planner.pick_action(obs)
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
            col = (
                "#00e676" if score >= 0.7
                else ("#ffd740" if score >= 0.5 else "#ff5252")
            )
            bar_w = score * 100
            rows += (
                f'<div style="margin:8px 0">'
                f'<div style="display:flex;justify-content:space-between;'
                f'font-size:0.85rem;margin-bottom:4px">'
                f'<span>{label.split("-")[0].strip()}</span>'
                f'<span style="color:{col};font-weight:700">{score:.4f}</span>'
                f'</div>'
                f'<div style="background:#1e3a5f;height:16px;border-radius:8px;'
                f'overflow:hidden">'
                f'<div style="background:{col};height:100%;width:{bar_w:.1f}%;'
                f'border-radius:8px;transition:width 0.5s ease"></div></div>'
                f'</div>'
            )

        avg = sum(results.values()) / max(len(results), 1)
        avg_col = (
            "#00e676" if avg >= 0.7
            else ("#ffd740" if avg >= 0.5 else "#ff5252")
        )

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

    with gr.Blocks() as dashboard:
        gr.HTML(f"<style>{CUSTOM_CSS}\n{TAB_OVERRIDE_CSS}</style>")

        with gr.Sidebar(position="left", open=True):
            gr.HTML(
                '<div style="font-size:1.1rem;font-weight:700;color:#40c4ff;'
                'margin-bottom:12px">\u2699 Controls</div>'
            )

            task_selector = gr.Dropdown(
                choices=list(TASK_INFO.keys()),
                value=list(TASK_INFO.keys())[0],
                label="Difficulty",
            )

            demo_btn = gr.Button(
                "\u25b6  Run Agent Demo",
                variant="primary",
                elem_classes="btn-demo",
            )

            speed_slider = gr.Slider(
                minimum=0.3, maximum=2.0, value=0.8, step=0.1,
                label="Demo Speed (seconds per step)",
            )

            gr.HTML('<hr style="border-color:#1e3a5f;margin:12px 0">')

            run_all_btn = gr.Button(
                "\u26a1 Run All Difficulties",
                variant="secondary",
                elem_classes="btn-demo-all",
            )

            gr.HTML('<hr style="border-color:#1e3a5f;margin:12px 0">')

            with gr.Accordion("\U0001f4cb Grading Rubric", open=False):
                gr.HTML(RUBRIC_HTML)

            gr.HTML(
                '<div style="font-size:0.78rem;color:#7a8ea0;margin-top:8px">'
                '\U0001f4a1 Use <b>Manual Control</b> panel below the '
                'shipments to test individual actions.</div>'
            )

        with gr.Column(elem_classes="mogul-root"):
            gr.HTML(INTRO_HTML)
            gr.HTML(HOW_IT_WORKS_HTML)

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

            narration_display = gr.HTML(
                value=(
                    '<div style="background:linear-gradient(135deg,#0d2137,#162332);'
                    'border:1px solid #1e3a5f;border-radius:10px;padding:20px;'
                    'margin:12px 0;text-align:center">'
                    '<span style="font-size:1.3rem">\U0001f3ac</span><br>'
                    '<span style="color:#7a8ea0;font-size:0.85rem">'
                    'Click <b style="color:#ff9100">\u25b6 Run Agent Demo</b> '
                    'in the sidebar to watch the agent solve shipments '
                    'step-by-step</span></div>'
                ),
            )

            with gr.Row():
                with gr.Column(scale=3):
                    gr.HTML(
                        '<div style="color:#7a8ea0;font-size:0.72rem;'
                        'text-transform:uppercase;letter-spacing:0.1em;'
                        'margin-bottom:6px">Shipments</div>'
                    )
                    shipments_display = gr.HTML(
                        value=(
                            '<div style="text-align:center;padding:40px;'
                            'color:#7a8ea0">'
                            '<div style="font-size:2rem;margin-bottom:8px">'
                            '\U0001f4e6</div>'
                            'Select a difficulty and click '
                            '<b>\u25b6 Run Agent Demo</b> in the sidebar '
                            'to watch the agent work.</div>'
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
                            '<div style="background:#0d2137;border:1px solid '
                            '#1e3a5f;padding:12px 16px;border-radius:6px;'
                            'font-family:monospace;font-size:0.82rem;'
                            'color:#40c4ff">Ready.</div>'
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

            # ── Manual Control Panel ──
            gr.HTML(
                '<div style="color:#40c4ff;font-size:0.88rem;font-weight:700;'
                'margin-top:20px;margin-bottom:8px;display:flex;'
                'align-items:center;gap:8px">'
                '<span style="font-size:1.1rem">\U0001f3ae</span>'
                'MANUAL CONTROL \u2014 Test Individual Actions'
                '</div>'
            )
            with gr.Group(elem_classes="manual-panel"):
                with gr.Row():
                    action_type = gr.Dropdown(
                        choices=sorted(ACTION_COSTS.keys()),
                        label="Action Type", value="investigate",
                        scale=2,
                    )
                    target_id = gr.Dropdown(
                        choices=[f"SHP-{i:03d}" for i in range(1, 9)],
                        label="Target Shipment", value="SHP-001",
                        scale=2,
                    )
                    params_input = gr.Textbox(
                        label="Parameters (JSON)", value="{}",
                        placeholder='{"reason": "urgent"}',
                        scale=2,
                    )
                    cost_hint = gr.HTML(
                        f'<div style="text-align:center;padding-top:24px">'
                        f'<div style="font-size:0.72rem;color:#7a8ea0;'
                        f'text-transform:uppercase;letter-spacing:0.05em">'
                        f'Action Cost</div>'
                        f'<div style="font-size:1.6rem;font-weight:700;'
                        f'color:#ffd740">'
                        f'${int(ACTION_COSTS.get("investigate", 0)):,}'
                        f'</div></div>',
                    )

                def _update_cost(at):
                    c = int(ACTION_COSTS.get(at, 0))
                    return (
                        f'<div style="text-align:center;padding-top:24px">'
                        f'<div style="font-size:0.72rem;color:#7a8ea0;'
                        f'text-transform:uppercase;letter-spacing:0.05em">'
                        f'Action Cost</div>'
                        f'<div style="font-size:1.6rem;font-weight:700;'
                        f'color:#ffd740">${c:,}</div></div>'
                    )

                action_type.change(
                    fn=_update_cost,
                    inputs=[action_type],
                    outputs=[cost_hint],
                )

                with gr.Row():
                    step_btn = gr.Button(
                        "\u26a1 Execute Step", variant="primary",
                        elem_classes="manual-execute-btn", scale=2,
                    )
                    reset_btn = gr.Button(
                        "\U0001f504 Reset Episode", variant="secondary",
                        elem_classes="manual-reset-btn", scale=1,
                    )

                gr.HTML(
                    '<div style="font-size:0.75rem;color:#7a8ea0;'
                    'margin-top:8px;line-height:1.5">'
                    '<b style="color:#e0e6ed">How to verify:</b> '
                    'Select a difficulty above \u2192 click '
                    '<b>\U0001f504 Reset</b> \u2192 '
                    'choose an action type & target \u2192 click '
                    '<b>\u26a1 Execute</b>. '
                    'Watch the shipment cards update in real-time. '
                    'Resolution actions: <code style="color:#00e676">'
                    'reroute, reschedule, file_claim, approve_refund, '
                    'split_shipment</code>.</div>'
                )

            scorecard_display = gr.HTML(value="")
            comparison_display = gr.HTML(value="")

            with gr.Accordion("\U0001f4c4 Raw JSON Response", open=False):
                raw_json = gr.Code(
                    value="", language="json", interactive=False,
                )

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
            return list(await do_reset(task_label))

        async def step_wrap(at, tid, params):
            return list(await do_step(at, tid, params))

        async def demo_wrap(task_label, speed):
            async for r in do_auto_run(task_label, speed):
                yield list(r)

        reset_btn.click(
            fn=reset_wrap, inputs=[task_selector], outputs=main_outputs,
        )
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

        dashboard.load(fn=None, js=AUTO_SWITCH_JS)

    return dashboard
