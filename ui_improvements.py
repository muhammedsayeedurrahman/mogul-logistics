"""
UI Improvements - Add to gradio_custom.py
This makes shipment-specific actions VISUALLY OBVIOUS
"""

# Add this CSS to highlight selected shipment
HIGHLIGHT_CSS = """
<style>
@keyframes highlight-pulse {
    0% { box-shadow: 0 0 0 0 rgba(255, 215, 64, 0.7); }
    50% { box-shadow: 0 0 0 10px rgba(255, 215, 64, 0); }
    100% { box-shadow: 0 0 0 0 rgba(255, 215, 64, 0); }
}

.shipment-selected {
    border: 3px solid #ffd740 !important;
    animation: highlight-pulse 2s infinite;
    background: linear-gradient(135deg, #1c1c1c, #2a2410) !important;
}

.shipment-updated {
    border: 3px solid #2B7D6D !important;
    animation: highlight-pulse 1s 3;
}
</style>
"""

# Modify render_shipments to accept last_acted_on parameter
def render_shipments(obs, last_acted_on=None):
    """
    Render shipment cards with highlighting for last affected shipment

    Args:
        obs: Observation dict
        last_acted_on: Shipment ID that was just acted on (e.g., "SHP-003")
    """
    # ... existing code ...

    for ship_id in shipments:
        # Add highlight class if this ship was just acted on
        card_class = "shipment-updated" if ship_id == last_acted_on else ""

        card_html = f'''
        <div class="{card_class}" style="
            border: {'3px solid #2B7D6D' if ship_id == last_acted_on else '1px solid #404040'};
            border-radius: 8px;
            padding: 12px;
            margin: 8px 0;
            transition: all 0.3s ease;
        ">
            <div style="display: flex; justify-content: space-between;">
                <strong style="color: {'#ffd740' if ship_id == last_acted_on else '#0668E1'}">
                    {ship_id}
                </strong>
                {f'<span style="color:#2B7D6D;font-size:0.75rem">✅ JUST UPDATED</span>' if ship_id == last_acted_on else ''}
            </div>
            <!-- rest of card -->
        </div>
        '''

# Add confirmation banner after each action
def action_confirmation_banner(ship_id, action_type, cost):
    """Show clear confirmation of what just happened"""
    return f'''
    <div style="
        background: linear-gradient(90deg, #0a2622, #1a3a35);
        border: 2px solid #2B7D6D;
        border-left: 5px solid #ffd740;
        border-radius: 10px;
        padding: 16px;
        margin: 12px 0;
        animation: slideIn 0.5s ease;
    ">
        <div style="display: flex; align-items: center; gap: 12px;">
            <span style="font-size: 2rem;">✅</span>
            <div style="flex: 1;">
                <div style="color: #2B7D6D; font-weight: 700; font-size: 1.1rem;">
                    Action Executed Successfully
                </div>
                <div style="color: #c8d6e0; font-size: 0.9rem; margin-top: 4px;">
                    <strong style="color: #ffd740;">{action_type.replace('_', ' ').title()}</strong>
                    performed on
                    <strong style="color: #ffd740;">{ship_id}</strong>
                    (Cost: ${cost})
                </div>
            </div>
        </div>
        <div style="
            background: #0a1612;
            padding: 10px;
            border-radius: 6px;
            margin-top: 12px;
            border-left: 3px solid #ffd740;
        ">
            <div style="color: #666; font-size: 0.75rem; margin-bottom: 4px;">
                📊 IMPACT
            </div>
            <div style="color: #c8d6e0; font-size: 0.85rem;">
                ✓ Only <strong style="color:#ffd740">{ship_id}</strong> was affected
                <br>
                ✓ Other shipments remain unchanged
                <br>
                ✓ Check the shipment card above to see the update
            </div>
        </div>
    </div>
    '''

# Add to do_step function:
async def do_step(action_type, target_id, params_str):
    # ... existing code ...

    # NEW: Create confirmation banner
    confirmation = action_confirmation_banner(target_id, action_type, cost)

    # NEW: Pass last_acted_on to render_shipments
    return (
        render_shipments(obs, last_acted_on=target_id),  # ← Highlight this ship
        *render_stats(obs),
        _wrap(obs.get("feedback", "")),
        "\n".join(action_log_entries),
        json.dumps(data, indent=2),
        scorecard,
        confirmation,  # ← Show confirmation banner
        render_route_map(obs),
    )
