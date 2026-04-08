"""Real-time constraint visualization for MOGUL Logistics.

Visualizes dynamic constraints:
- Budget consumption (spending rate, forecast)
- Time remaining (countdown, steps left)
- SLA deadlines (color-coded urgency zones)
- Active constraints (which ones are binding)
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta


def render_budget_constraint(
    budget_remaining: float,
    budget_initial: float,
    steps_taken: int
) -> str:
    """Render budget constraint with spending rate and forecast."""
    budget_used = budget_initial - budget_remaining
    usage_pct = (budget_used / budget_initial) * 100

    # Calculate spending rate
    if steps_taken > 0:
        avg_spend_per_step = budget_used / steps_taken
        forecast_steps = int(budget_remaining / avg_spend_per_step) if avg_spend_per_step > 0 else 999
    else:
        avg_spend_per_step = 0
        forecast_steps = 999

    # Color based on usage
    if usage_pct < 50:
        color = "#4CAF50"  # Green
        status = "HEALTHY"
    elif usage_pct < 75:
        color = "#FF9800"  # Orange
        status = "MODERATE"
    else:
        color = "#f44336"  # Red
        status = "CRITICAL"

    return f"""
    <div style="background:rgba(0,0,0,0.3);backdrop-filter:blur(10px);border-radius:12px;padding:16px;margin-bottom:12px;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
            <span style="font-size:14px;font-weight:600;color:#fff;">💰 Budget Constraint</span>
            <span style="font-size:12px;color:{color};font-weight:600;">{status}</span>
        </div>

        <!-- Progress bar -->
        <div style="background:rgba(255,255,255,0.1);border-radius:8px;height:24px;position:relative;overflow:hidden;margin-bottom:8px;">
            <div style="background:{color};height:100%;width:{usage_pct:.1f}%;transition:width 0.5s ease;"></div>
            <div style="position:absolute;top:0;left:0;right:0;bottom:0;display:flex;align-items:center;justify-content:center;color:#fff;font-size:12px;font-weight:600;">
                ${budget_used:,.0f} / ${budget_initial:,.0f} ({usage_pct:.1f}%)
            </div>
        </div>

        <!-- Metrics -->
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;font-size:11px;">
            <div style="background:rgba(255,255,255,0.05);padding:6px;border-radius:6px;text-align:center;">
                <div style="color:#999;">Remaining</div>
                <div style="color:#fff;font-weight:600;">${budget_remaining:,.0f}</div>
            </div>
            <div style="background:rgba(255,255,255,0.05);padding:6px;border-radius:6px;text-align:center;">
                <div style="color:#999;">Avg/Step</div>
                <div style="color:#fff;font-weight:600;">${avg_spend_per_step:,.0f}</div>
            </div>
            <div style="background:rgba(255,255,255,0.05);padding:6px;border-radius:6px;text-align:center;">
                <div style="color:#999;">Forecast Steps</div>
                <div style="color:#fff;font-weight:600;">{forecast_steps}</div>
            </div>
        </div>
    </div>
    """


def render_time_constraint(
    time_remaining: int,
    time_initial: int
) -> str:
    """Render time constraint with countdown."""
    time_used = time_initial - time_remaining
    usage_pct = (time_used / time_initial) * 100

    # Color based on usage
    if usage_pct < 50:
        color = "#4CAF50"
        status = "ON TRACK"
    elif usage_pct < 75:
        color = "#FF9800"
        status = "MODERATE"
    else:
        color = "#f44336"
        status = "URGENT"

    return f"""
    <div style="background:rgba(0,0,0,0.3);backdrop-filter:blur(10px);border-radius:12px;padding:16px;margin-bottom:12px;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
            <span style="font-size:14px;font-weight:600;color:#fff;">⏰ Time Constraint</span>
            <span style="font-size:12px;color:{color};font-weight:600;">{status}</span>
        </div>

        <!-- Progress bar -->
        <div style="background:rgba(255,255,255,0.1);border-radius:8px;height:24px;position:relative;overflow:hidden;margin-bottom:8px;">
            <div style="background:{color};height:100%;width:{usage_pct:.1f}%;transition:width 0.5s ease;"></div>
            <div style="position:absolute;top:0;left:0;right:0;bottom:0;display:flex;align-items:center;justify-content:center;color:#fff;font-size:12px;font-weight:600;">
                {time_used} / {time_initial} steps ({usage_pct:.1f}%)
            </div>
        </div>

        <!-- Metrics -->
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;font-size:11px;">
            <div style="background:rgba(255,255,255,0.05);padding:6px;border-radius:6px;text-align:center;">
                <div style="color:#999;">Steps Remaining</div>
                <div style="color:#fff;font-weight:600;font-size:16px;">{time_remaining}</div>
            </div>
            <div style="background:rgba(255,255,255,0.05);padding:6px;border-radius:6px;text-align:center;">
                <div style="color:#999;">Steps Used</div>
                <div style="color:#fff;font-weight:600;font-size:16px;">{time_used}</div>
            </div>
        </div>
    </div>
    """


def render_sla_constraints(
    shipments: List[Dict[str, Any]]
) -> str:
    """Render SLA deadlines with color-coded urgency zones."""
    if not shipments:
        return ""

    # Sort by SLA urgency
    sorted_shipments = sorted(shipments, key=lambda s: s.get("sla_deadline_hours", 999))

    rows = []
    for ship in sorted_shipments:
        sid = ship["tracking_id"]
        sla_hours = ship.get("sla_deadline_hours", 0)
        status = ship.get("status", "unknown")

        # Color zones
        if sla_hours < 12:
            zone_color = "#f44336"  # Red - Critical
            zone_label = "CRITICAL"
        elif sla_hours < 24:
            zone_color = "#FF9800"  # Orange - Warning
            zone_label = "WARNING"
        elif sla_hours < 48:
            zone_color = "#FFC107"  # Yellow - Caution
            zone_label = "CAUTION"
        else:
            zone_color = "#4CAF50"  # Green - Safe
            zone_label = "SAFE"

        rows.append(f"""
        <div style="background:rgba(255,255,255,0.05);border-left:3px solid {zone_color};padding:8px;margin-bottom:6px;border-radius:6px;">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <div style="flex:1;">
                    <div style="font-size:12px;font-weight:600;color:#fff;">{sid}</div>
                    <div style="font-size:10px;color:#999;margin-top:2px;">{status}</div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:14px;font-weight:600;color:{zone_color};">{sla_hours:.0f}h</div>
                    <div style="font-size:9px;color:{zone_color};margin-top:2px;">{zone_label}</div>
                </div>
            </div>
        </div>
        """)

    return f"""
    <div style="background:rgba(0,0,0,0.3);backdrop-filter:blur(10px);border-radius:12px;padding:16px;margin-bottom:12px;">
        <div style="font-size:14px;font-weight:600;color:#fff;margin-bottom:12px;">🎯 SLA Constraints</div>
        <div style="max-height:200px;overflow-y:auto;">
            {''.join(rows)}
        </div>
    </div>
    """


def render_active_constraints(
    obs: Dict[str, Any]
) -> str:
    """Identify and highlight which constraints are currently binding."""
    budget_remaining = obs.get("budget_remaining", 0)
    time_remaining = obs.get("time_remaining", 0)
    shipments = obs.get("shipments", [])

    constraints = []

    # Check budget constraint
    if budget_remaining < 2000:
        constraints.append({
            "name": "Budget",
            "severity": "CRITICAL" if budget_remaining < 1000 else "HIGH",
            "message": f"Only ${budget_remaining:,.0f} remaining",
            "icon": "💰",
            "color": "#f44336" if budget_remaining < 1000 else "#FF9800"
        })

    # Check time constraint
    if time_remaining < 5:
        constraints.append({
            "name": "Time",
            "severity": "CRITICAL" if time_remaining < 3 else "HIGH",
            "message": f"Only {time_remaining} steps remaining",
            "icon": "⏰",
            "color": "#f44336" if time_remaining < 3 else "#FF9800"
        })

    # Check SLA constraints
    critical_slas = [s for s in shipments if s.get("sla_deadline_hours", 999) < 12]
    if critical_slas:
        constraints.append({
            "name": "SLA",
            "severity": "CRITICAL",
            "message": f"{len(critical_slas)} shipment(s) at critical SLA",
            "icon": "🎯",
            "color": "#f44336"
        })

    if not constraints:
        return f"""
        <div style="background:rgba(76,175,80,0.1);border:1px solid #4CAF50;border-radius:12px;padding:12px;text-align:center;">
            <div style="font-size:16px;margin-bottom:4px;">✅</div>
            <div style="font-size:12px;color:#4CAF50;font-weight:600;">All Constraints Satisfied</div>
        </div>
        """

    rows = []
    for c in constraints:
        rows.append(f"""
        <div style="background:rgba(255,255,255,0.05);border-left:3px solid {c['color']};padding:10px;margin-bottom:8px;border-radius:6px;">
            <div style="display:flex;align-items:center;gap:8px;">
                <div style="font-size:18px;">{c['icon']}</div>
                <div style="flex:1;">
                    <div style="font-size:12px;font-weight:600;color:#fff;">{c['name']} Constraint</div>
                    <div style="font-size:10px;color:#999;margin-top:2px;">{c['message']}</div>
                </div>
                <div style="font-size:10px;color:{c['color']};font-weight:600;background:rgba(255,255,255,0.1);padding:4px 8px;border-radius:4px;">
                    {c['severity']}
                </div>
            </div>
        </div>
        """)

    return f"""
    <div style="background:rgba(0,0,0,0.3);backdrop-filter:blur(10px);border-radius:12px;padding:16px;margin-bottom:12px;">
        <div style="font-size:14px;font-weight:600;color:#fff;margin-bottom:12px;">🚨 Active Constraints</div>
        {''.join(rows)}
    </div>
    """


def render_all_constraints(
    obs: Dict[str, Any],
    initial_budget: float,
    initial_time: int
) -> str:
    """Render complete constraint visualization panel."""
    budget_remaining = obs.get("budget_remaining", initial_budget)
    time_remaining = obs.get("time_remaining", initial_time)
    shipments = obs.get("shipments", [])

    steps_taken = initial_time - time_remaining

    return f"""
    <div style="padding:16px;background:linear-gradient(135deg,rgba(238,76,44,0.05),rgba(238,76,44,0.1));border-radius:16px;">
        <div style="font-size:18px;font-weight:700;color:#EE4C2C;margin-bottom:16px;display:flex;align-items:center;gap:8px;">
            <span>📊</span>
            <span>Live Constraint Monitor</span>
        </div>

        {render_active_constraints(obs)}
        {render_budget_constraint(budget_remaining, initial_budget, steps_taken)}
        {render_time_constraint(time_remaining, initial_time)}
        {render_sla_constraints(shipments)}
    </div>
    """
