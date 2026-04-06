"""Route map visualization using pure SVG — shows Indian logistics network.

Uses inline SVG instead of Plotly to work inside Gradio's gr.HTML component
(which strips <script> tags and blocks external JS).

Always renders the base network; overlays shipment routes when an episode is active.
"""

from __future__ import annotations

import re

# Approximate lat/lng for Indian logistics hubs
CITY_COORDS: dict[str, tuple[float, float]] = {
    "Mumbai": (19.08, 72.88),
    "Delhi NCR": (28.61, 77.21),
    "Chennai": (13.08, 80.27),
    "Bangalore": (12.97, 77.59),
    "Kolkata": (22.57, 88.36),
    "Hyderabad": (17.38, 78.49),
    "Pune": (18.52, 73.86),
    "Ahmedabad": (23.02, 72.57),
    "Jaipur": (26.91, 75.79),
    "Lucknow": (26.85, 80.95),
}

_STATUS_COLORS = {
    "resolved": "#00e676",
    "failed": "#ff5252",
    "investigating": "#40c4ff",
    "action_taken": "#ff9100",
    "new": "#7a8ea0",
}

_STATUS_LABELS = {
    "resolved": "Resolved",
    "failed": "Failed",
    "investigating": "Investigating",
    "action_taken": "Action Taken",
    "new": "New",
}

_SHIP_RE = re.compile(
    r"(SHP-\d+):\s+\S+\s+\|\s+status=(\w+)\s+\|\s+priority=(\w+)"
    r"\s+\|\s+progress=(\d+)%\s+\|\s+SLA in (\d+) steps"
)

# SVG viewport dimensions
_W = 600
_H = 420
_PAD = 40

# Geo bounding box for India (lat/lng)
_LAT_MIN = 10.0
_LAT_MAX = 30.0
_LNG_MIN = 70.0
_LNG_MAX = 92.0


def _geo_to_svg(lat: float, lng: float) -> tuple[float, float]:
    """Convert lat/lng to SVG x/y coordinates."""
    x = _PAD + (lng - _LNG_MIN) / (_LNG_MAX - _LNG_MIN) * (_W - 2 * _PAD)
    y = _PAD + (1 - (lat - _LAT_MIN) / (_LAT_MAX - _LAT_MIN)) * (_H - 2 * _PAD)
    return x, y


def _render_base_network() -> list[str]:
    """Render the base Indian logistics network (cities + edges)."""
    cities = list(CITY_COORDS.keys())
    parts: list[str] = []

    # Background network edges (nearby city pairs)
    for i, c1 in enumerate(cities):
        for c2 in cities[i + 1:]:
            lat1, lon1 = CITY_COORDS[c1]
            lat2, lon2 = CITY_COORDS[c2]
            dist = ((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2) ** 0.5
            if dist < 8:
                x1, y1 = _geo_to_svg(lat1, lon1)
                x2, y2 = _geo_to_svg(lat2, lon2)
                parts.append(
                    f'<line x1="{x1:.1f}" y1="{y1:.1f}" '
                    f'x2="{x2:.1f}" y2="{y2:.1f}" '
                    f'stroke="#1e3a5f" stroke-width="0.8" stroke-dasharray="4,4" '
                    f'opacity="0.5"/>'
                )

    # Hub nodes with labels
    for name, (lat, lng) in CITY_COORDS.items():
        cx, cy = _geo_to_svg(lat, lng)
        # Outer glow for hub
        parts.append(
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="8" '
            f'fill="#40c4ff" opacity="0.08"/>'
        )
        parts.append(
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="4" '
            f'fill="#0d2137" stroke="#40c4ff" stroke-width="1.5"/>'
        )
        parts.append(
            f'<text x="{cx:.1f}" y="{cy - 10:.1f}" '
            f'text-anchor="middle" fill="#7a8ea0" '
            f'font-size="9" font-family="sans-serif">{name}</text>'
        )

    return parts


def render_route_map(obs: dict | None = None, scenario_shipments: list | None = None) -> str:
    """Render an SVG route map showing shipment status on Indian geography.

    Always shows the base network. Overlays shipment routes when an episode
    is active. Returns HTML with inline SVG for Gradio's gr.HTML.
    """
    if obs is None:
        obs = {}

    status_text = obs.get("shipment_status", "")

    # Parse shipments from observation
    ships = []
    for m in _SHIP_RE.finditer(status_text):
        ships.append({
            "id": m.group(1),
            "status": m.group(2),
            "priority": m.group(3),
            "progress": int(m.group(4)) / 100.0,
            "sla": int(m.group(5)),
        })

    cities = list(CITY_COORDS.keys())
    svg_parts: list[str] = []

    # SVG header
    svg_parts.append(
        f'<svg viewBox="0 0 {_W} {_H}" xmlns="http://www.w3.org/2000/svg" '
        f'style="width:100%;height:auto;background:#0f1923;border-radius:8px">'
    )

    # Title
    svg_parts.append(
        f'<text x="{_W / 2}" y="18" text-anchor="middle" fill="#7a8ea0" '
        f'font-size="10" font-family="sans-serif" letter-spacing="0.1em">'
        f'INDIAN LOGISTICS NETWORK</text>'
    )

    # Always draw the base network
    svg_parts.extend(_render_base_network())

    # Overlay shipment routes if episode is active
    if ships:
        for i, ship in enumerate(ships):
            origin_city = cities[i % len(cities)]
            dest_city = cities[(i + 3) % len(cities)]
            if origin_city == dest_city:
                dest_city = cities[(i + 5) % len(cities)]

            lat1, lon1 = CITY_COORDS[origin_city]
            lat2, lon2 = CITY_COORDS[dest_city]
            x1, y1 = _geo_to_svg(lat1, lon1)
            x2, y2 = _geo_to_svg(lat2, lon2)
            color = _STATUS_COLORS.get(ship["status"], "#7a8ea0")

            # Route line glow
            svg_parts.append(
                f'<line x1="{x1:.1f}" y1="{y1:.1f}" '
                f'x2="{x2:.1f}" y2="{y2:.1f}" '
                f'stroke="{color}" stroke-width="2.5" opacity="0.3"/>'
            )
            # Route line
            svg_parts.append(
                f'<line x1="{x1:.1f}" y1="{y1:.1f}" '
                f'x2="{x2:.1f}" y2="{y2:.1f}" '
                f'stroke="{color}" stroke-width="1.5"/>'
            )

            # Shipment marker at interpolated position
            prog = max(0.1, ship["progress"])
            mx = x1 + (x2 - x1) * prog
            my = y1 + (y2 - y1) * prog
            r = 8 if ship["priority"] in ("critical", "high") else 6

            # Outer glow
            svg_parts.append(
                f'<circle cx="{mx:.1f}" cy="{my:.1f}" r="{r + 4}" '
                f'fill="{color}" opacity="0.15"/>'
            )
            # Main marker
            svg_parts.append(
                f'<circle cx="{mx:.1f}" cy="{my:.1f}" r="{r}" '
                f'fill="{color}" stroke="white" stroke-width="1.5"/>'
            )
            # Ship ID label
            svg_parts.append(
                f'<text x="{mx:.1f}" y="{my + r + 12:.1f}" '
                f'text-anchor="middle" fill="{color}" '
                f'font-size="8" font-family="monospace" font-weight="bold">'
                f'{ship["id"]}</text>'
            )
    else:
        # No active episode — show prompt text on the map
        svg_parts.append(
            f'<text x="{_W / 2}" y="{_H / 2}" text-anchor="middle" '
            f'fill="#7a8ea0" font-size="11" font-family="sans-serif" opacity="0.7">'
            f'Run an episode to see live shipment tracking</text>'
        )

    svg_parts.append("</svg>")

    # Build legend below the map (only when shipments exist)
    legend_html = ""
    if ships:
        legend_items = []
        for ship in ships:
            color = _STATUS_COLORS.get(ship["status"], "#7a8ea0")
            label = _STATUS_LABELS.get(ship["status"], ship["status"])
            pct = int(ship["progress"] * 100)
            sla_color = "#ff5252" if ship["sla"] <= 2 else "#ffd740" if ship["sla"] <= 4 else "#00e676"
            legend_items.append(
                f'<div style="display:flex;align-items:center;gap:8px;padding:6px 10px;'
                f'background:#0d1520;border:1px solid #1e3a5f;border-left:3px solid {color};'
                f'border-radius:4px;font-size:0.78rem">'
                f'<span style="color:{color};font-weight:700;font-family:monospace">'
                f'{ship["id"]}</span>'
                f'<span style="color:#e0e6ed">{label}</span>'
                f'<span style="color:#7a8ea0">{pct}%</span>'
                f'<span style="color:{sla_color};font-weight:600">SLA:{ship["sla"]}</span>'
                f'<span style="color:#7a8ea0;font-size:0.7rem">{ship["priority"]}</span>'
                f'</div>'
            )
        legend_html = (
            f'<div style="display:flex;flex-wrap:wrap;gap:6px;margin-top:8px">'
            f'{"".join(legend_items)}</div>'
        )

    return (
        f'<div style="background:#0f1923;border:1px solid #1e3a5f;'
        f'border-radius:10px;padding:12px;overflow:hidden">'
        f'{"".join(svg_parts)}'
        f'{legend_html}'
        f'</div>'
    )
