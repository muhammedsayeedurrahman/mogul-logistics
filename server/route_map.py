"""Route map visualization using Plotly — shows Indian logistics network."""

from __future__ import annotations

import json
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

_SHIP_RE = re.compile(
    r"(SHP-\d+):\s+\S+\s+\|\s+status=(\w+)\s+\|\s+priority=(\w+)"
    r"\s+\|\s+progress=(\d+)%\s+\|\s+SLA in (\d+) steps"
)


def render_route_map(obs: dict, scenario_shipments: list | None = None) -> str:
    """Render an HTML route map showing shipment status on Indian geography.

    Returns an HTML string with an embedded Plotly figure, or a placeholder
    if plotly is not available.
    """
    try:
        import plotly.graph_objects as go
    except ImportError:
        return (
            '<div style="text-align:center;padding:40px;color:#7a8ea0">'
            "Route map requires plotly. Install with: pip install plotly</div>"
        )

    status_text = obs.get("shipment_status", "")
    progress_map = obs.get("resolution_progress", {})

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

    if not ships:
        return (
            '<div style="text-align:center;padding:30px;color:#7a8ea0;'
            'font-size:0.85rem">'
            "Start an episode to see the route map.</div>"
        )

    fig = go.Figure()

    # Draw background network edges (all city pairs that are adjacent)
    cities = list(CITY_COORDS.keys())
    for i, c1 in enumerate(cities):
        for c2 in cities[i + 1 :]:
            lat1, lon1 = CITY_COORDS[c1]
            lat2, lon2 = CITY_COORDS[c2]
            dist = ((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2) ** 0.5
            if dist < 8:  # Only draw nearby connections
                fig.add_trace(go.Scattergeo(
                    lat=[lat1, lat2],
                    lon=[lon1, lon2],
                    mode="lines",
                    line=dict(width=0.5, color="#1e3a5f"),
                    showlegend=False,
                    hoverinfo="skip",
                ))

    # Draw hub nodes
    hub_lats = [c[0] for c in CITY_COORDS.values()]
    hub_lons = [c[1] for c in CITY_COORDS.values()]
    fig.add_trace(go.Scattergeo(
        lat=hub_lats,
        lon=hub_lons,
        text=list(CITY_COORDS.keys()),
        mode="markers+text",
        marker=dict(size=6, color="#1e3a5f", line=dict(width=1, color="#40c4ff")),
        textposition="top center",
        textfont=dict(size=9, color="#7a8ea0"),
        showlegend=False,
        hoverinfo="text",
    ))

    # Assign cities to shipments deterministically
    for i, ship in enumerate(ships):
        origin_city = cities[i % len(cities)]
        dest_city = cities[(i + 3) % len(cities)]
        if origin_city == dest_city:
            dest_city = cities[(i + 5) % len(cities)]

        lat1, lon1 = CITY_COORDS[origin_city]
        lat2, lon2 = CITY_COORDS[dest_city]
        color = _STATUS_COLORS.get(ship["status"], "#7a8ea0")

        # Route line
        fig.add_trace(go.Scattergeo(
            lat=[lat1, lat2],
            lon=[lon1, lon2],
            mode="lines",
            line=dict(width=2.5, color=color),
            showlegend=False,
            hoverinfo="text",
            hovertext=f"{ship['id']}: {origin_city} → {dest_city}",
        ))

        # Shipment marker at interpolated position based on progress
        prog = ship["progress"]
        mid_lat = lat1 + (lat2 - lat1) * max(0.1, prog)
        mid_lon = lon1 + (lon2 - lon1) * max(0.1, prog)

        marker_size = 14 if ship["priority"] in ("critical", "high") else 10
        fig.add_trace(go.Scattergeo(
            lat=[mid_lat],
            lon=[mid_lon],
            mode="markers+text",
            marker=dict(
                size=marker_size,
                color=color,
                symbol="circle",
                line=dict(width=1.5, color="white"),
            ),
            text=[ship["id"]],
            textposition="bottom center",
            textfont=dict(size=8, color=color, family="monospace"),
            showlegend=False,
            hoverinfo="text",
            hovertext=(
                f"<b>{ship['id']}</b><br>"
                f"Status: {ship['status']}<br>"
                f"Progress: {ship['progress']:.0%}<br>"
                f"Priority: {ship['priority']}<br>"
                f"SLA: {ship['sla']} steps<br>"
                f"Route: {origin_city} → {dest_city}"
            ),
        ))

    fig.update_geos(
        scope="asia",
        center=dict(lat=22, lon=78),
        projection_scale=4.5,
        showland=True,
        landcolor="#0d1520",
        showocean=True,
        oceancolor="#0a0f18",
        showlakes=False,
        showcountries=True,
        countrycolor="#1e3a5f",
        showcoastlines=True,
        coastlinecolor="#1e3a5f",
        bgcolor="#0f1923",
    )

    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        height=380,
        paper_bgcolor="#0f1923",
        plot_bgcolor="#0f1923",
        font=dict(color="#e0e6ed"),
    )

    html = fig.to_html(
        include_plotlyjs="cdn",
        full_html=False,
        config={"displayModeBar": False},
    )
    return (
        f'<div style="border:1px solid #1e3a5f;border-radius:8px;overflow:hidden;'
        f'background:#0f1923">{html}</div>'
    )
