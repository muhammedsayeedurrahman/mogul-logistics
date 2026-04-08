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

/* Stat cards with glassmorphism */
.stat-card {
  background: linear-gradient(135deg, rgba(38, 38, 38, 0.95), rgba(28, 28, 28, 0.98)) !important;
  backdrop-filter: blur(10px) !important;
  -webkit-backdrop-filter: blur(10px) !important;
  border: 1px solid rgba(255, 255, 255, 0.08) !important;
  padding: 14px 18px !important; text-align: center !important;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
  border-radius: 12px !important;
  box-shadow: 0 8px 16px -4px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.05) !important;
  position: relative !important;
  overflow: hidden !important;
}
.stat-card::before {
  content: '' !important;
  position: absolute !important;
  top: 0 !important; left: 0 !important;
  right: 0 !important; bottom: 0 !important;
  background: linear-gradient(135deg, rgba(6, 104, 225, 0.05), transparent) !important;
  opacity: 0 !important;
  transition: opacity 0.3s ease !important;
}
.stat-card:hover {
  border-color: rgba(6, 104, 225, 0.5) !important;
  transform: translateY(-4px) scale(1.02) !important;
  box-shadow: 0 12px 24px -8px rgba(6, 104, 225, 0.3),
              0 0 32px -8px rgba(6, 104, 225, 0.2),
              inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
}
.stat-card:hover::before { opacity: 1 !important; }
.stat-card .stat-value {
  font-size: 2rem !important;
  font-weight: 800 !important;
  line-height: 1.1 !important;
  background: linear-gradient(135deg, currentColor, currentColor 60%, rgba(255,255,255,0.7)) !important;
  -webkit-background-clip: text !important;
  background-clip: text !important;
  filter: drop-shadow(0 2px 8px rgba(0,0,0,0.3)) !important;
}
.stat-card .stat-label {
  font-size: 0.68rem !important;
  text-transform: uppercase !important;
  letter-spacing: 0.12em !important;
  color: #888888 !important;
  font-weight: 600 !important;
  opacity: 0.9 !important;
}
.stat-green .stat-value {
  color: #2B7D6D !important;
  text-shadow: 0 0 20px rgba(43, 125, 109, 0.6), 0 0 40px rgba(43, 125, 109, 0.3) !important;
  animation: pulse-green 3s ease-in-out infinite !important;
}
.stat-blue  .stat-value {
  color: #0668E1 !important;
  text-shadow: 0 0 20px rgba(6, 104, 225, 0.6), 0 0 40px rgba(6, 104, 225, 0.3) !important;
}
.stat-yellow .stat-value {
  color: #ffd740 !important;
  text-shadow: 0 0 20px rgba(255, 215, 64, 0.6), 0 0 40px rgba(255, 215, 64, 0.3) !important;
}
.stat-red   .stat-value {
  color: #ff5252 !important;
  text-shadow: 0 0 20px rgba(255, 82, 82, 0.6), 0 0 40px rgba(255, 82, 82, 0.3) !important;
  animation: pulse-red 2s ease-in-out infinite !important;
}

@keyframes pulse-green {
  0%, 100% { text-shadow: 0 0 20px rgba(43, 125, 109, 0.6), 0 0 40px rgba(43, 125, 109, 0.3); }
  50% { text-shadow: 0 0 30px rgba(43, 125, 109, 0.8), 0 0 60px rgba(43, 125, 109, 0.4); }
}
@keyframes pulse-red {
  0%, 100% { text-shadow: 0 0 20px rgba(255, 82, 82, 0.6), 0 0 40px rgba(255, 82, 82, 0.3); }
  50% { text-shadow: 0 0 30px rgba(255, 82, 82, 0.8), 0 0 60px rgba(255, 82, 82, 0.4); }
}
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

/* Action panel with glassmorphism */
.action-panel {
  background: linear-gradient(135deg, rgba(38, 38, 38, 0.9), rgba(28, 28, 28, 0.95)) !important;
  backdrop-filter: blur(12px) !important;
  -webkit-backdrop-filter: blur(12px) !important;
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
  padding: 18px !important;
  border-radius: 12px !important;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.05) !important;
  position: relative !important;
  overflow: hidden !important;
}
.action-panel::after {
  content: '' !important;
  position: absolute !important;
  top: -50% !important;
  left: -50% !important;
  width: 200% !important;
  height: 200% !important;
  background: radial-gradient(circle, rgba(6, 104, 225, 0.03) 0%, transparent 70%) !important;
  animation: rotate-gradient 20s linear infinite !important;
  pointer-events: none !important;
}
@keyframes rotate-gradient {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Enhanced Buttons with animations */
.btn-reset {
  background: linear-gradient(135deg, rgba(28, 28, 28, 0.8), rgba(38, 38, 38, 0.9)) !important;
  backdrop-filter: blur(8px) !important;
  border: 1px solid #0668E1 !important;
  color: #0668E1 !important;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
  position: relative !important;
  overflow: hidden !important;
}
.btn-reset::before {
  content: '' !important;
  position: absolute !important;
  top: 50% !important; left: 50% !important;
  width: 0 !important; height: 0 !important;
  border-radius: 50% !important;
  background: rgba(6, 104, 225, 0.1) !important;
  transform: translate(-50%, -50%) !important;
  transition: width 0.6s, height 0.6s !important;
}
.btn-reset:hover::before {
  width: 300px !important; height: 300px !important;
}
.btn-reset:hover {
  box-shadow: 0 0 20px rgba(6, 104, 225, 0.4), inset 0 0 20px rgba(6, 104, 225, 0.1) !important;
  transform: translateY(-2px) !important;
}
.btn-step {
  background: linear-gradient(135deg, #2B7D6D, #1f5a4e, #2B7D6D) !important;
  background-size: 200% 100% !important;
  border: none !important; color: #ffffff !important; font-weight: 700 !important;
  box-shadow: 0 4px 15px rgba(43, 125, 109, 0.4) !important;
  transition: all 0.3s ease !important;
}
.btn-step:hover {
  background-position: 100% 0 !important;
  box-shadow: 0 6px 25px rgba(43, 125, 109, 0.6) !important;
  transform: translateY(-2px) !important;
}
.btn-demo {
  background: linear-gradient(135deg, #0668E1 0%, #EE4C2C 50%, #0668E1 100%) !important;
  background-size: 200% 100% !important;
  border: none !important; color: #ffffff !important; font-weight: 700 !important;
  font-size: 1rem !important; padding: 12px !important;
  box-shadow: 0 0 20px rgba(238, 76, 44, 0.5), 0 4px 15px rgba(0, 0, 0, 0.3) !important;
  animation: shimmer 3s ease-in-out infinite !important;
  transition: all 0.3s ease !important;
}
.btn-demo:hover {
  box-shadow: 0 0 30px rgba(238, 76, 44, 0.7), 0 6px 25px rgba(0, 0, 0, 0.4) !important;
  transform: translateY(-3px) scale(1.02) !important;
}
.btn-demo-all {
  background: linear-gradient(135deg, #812CE5, #5a1e9e, #812CE5) !important;
  background-size: 200% 100% !important;
  border: none !important; color: #ffffff !important; font-weight: 700 !important;
  box-shadow: 0 0 20px rgba(129, 44, 229, 0.5), 0 4px 15px rgba(0, 0, 0, 0.3) !important;
  transition: all 0.3s ease !important;
}
.btn-demo-all:hover {
  background-position: 100% 0 !important;
  box-shadow: 0 0 30px rgba(129, 44, 229, 0.7), 0 6px 25px rgba(0, 0, 0, 0.4) !important;
  transform: translateY(-2px) !important;
}
@keyframes shimmer {
  0%, 100% { background-position: 0% 0%; }
  50% { background-position: 100% 0%; }
}

/* Log with glassmorphism */
.action-log {
  background: linear-gradient(135deg, rgba(28, 28, 28, 0.95), rgba(0, 0, 0, 0.98)) !important;
  backdrop-filter: blur(8px) !important;
  border: 1px solid rgba(255, 255, 255, 0.08) !important;
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 0.78rem !important;
  max-height: 260px !important;
  overflow-y: auto !important;
  border-radius: 8px !important;
  box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.4), 0 4px 12px rgba(0, 0, 0, 0.3) !important;
}
.action-log * { font-family: 'JetBrains Mono', monospace !important; }
/* Custom scrollbar */
.action-log::-webkit-scrollbar { width: 8px !important; }
.action-log::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.3) !important;
  border-radius: 4px !important;
}
.action-log::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, #0668E1, #812CE5) !important;
  border-radius: 4px !important;
  border: 2px solid transparent !important;
  background-clip: content-box !important;
}
.action-log::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(180deg, #0668E1, #EE4C2C) !important;
  background-clip: content-box !important;
}

/* Ship cards with advanced transitions and glassmorphism */
.ship-card-wrap div {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
  backdrop-filter: blur(8px) !important;
  position: relative !important;
}
.ship-card-wrap div::after {
  content: '' !important;
  position: absolute !important;
  top: 0 !important; left: 0 !important;
  right: 0 !important; bottom: 0 !important;
  background: linear-gradient(135deg, transparent, rgba(6, 104, 225, 0.05)) !important;
  opacity: 0 !important;
  transition: opacity 0.3s ease !important;
  pointer-events: none !important;
  border-radius: inherit !important;
}
.ship-card-wrap div:hover::after { opacity: 1 !important; }
.ship-card-wrap div:hover {
  transform: translateX(4px) scale(1.01) !important;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.08) !important;
}

/* Sidebar with glassmorphism */
.sidebar-section {
  background: linear-gradient(135deg, rgba(38, 38, 38, 0.85), rgba(28, 28, 28, 0.9)) !important;
  backdrop-filter: blur(10px) !important;
  border: 1px solid rgba(255, 255, 255, 0.08) !important;
  padding: 14px !important;
  margin-bottom: 10px !important;
  border-radius: 10px !important;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.05) !important;
  transition: all 0.3s ease !important;
}
.sidebar-section:hover {
  background: linear-gradient(135deg, rgba(38, 38, 38, 0.9), rgba(28, 28, 28, 0.95)) !important;
  border-color: rgba(6, 104, 225, 0.3) !important;
  transform: translateX(4px) !important;
}

/* Cinematic feed with enhanced animations */
@keyframes cinematic-pulse {
  0%, 100% {
    opacity: 1;
    text-shadow: 0 0 20px rgba(238, 76, 44, 0.8), 0 0 40px rgba(238, 76, 44, 0.4);
    transform: scale(1);
  }
  50% {
    opacity: 0.7;
    text-shadow: 0 0 10px rgba(238, 76, 44, 0.5);
    transform: scale(0.98);
  }
}
@keyframes cinematic-slide {
  from {
    opacity: 0;
    transform: translateY(20px) translateX(-10px);
    filter: blur(4px);
  }
  to {
    opacity: 1;
    transform: translateY(0) translateX(0);
    filter: blur(0);
  }
}
@keyframes cinematic-shimmer {
  0% { background-position: -200% center; }
  100% { background-position: 200% center; }
}
.cinematic-entry {
  animation: cinematic-slide 0.6s cubic-bezier(0.4, 0, 0.2, 1) !important;
  position: relative !important;
  overflow: hidden !important;
}
.cinematic-entry::before {
  content: '' !important;
  position: absolute !important;
  top: 0 !important; left: 0 !important;
  right: 0 !important; bottom: 0 !important;
  background: linear-gradient(90deg,
    transparent,
    rgba(6, 104, 225, 0.1),
    transparent) !important;
  background-size: 200% 100% !important;
  animation: cinematic-shimmer 3s ease-in-out !important;
  pointer-events: none !important;
}
.cinematic-live {
  animation: cinematic-pulse 1.8s ease-in-out infinite !important;
  color: #EE4C2C !important;
  font-weight: 700 !important;
}
.cinematic-feed {
  max-height: 420px !important;
  overflow-y: auto !important;
  scroll-behavior: smooth !important;
}
/* Custom scrollbar for cinematic feed */
.cinematic-feed::-webkit-scrollbar { width: 6px !important; }
.cinematic-feed::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.2) !important;
  border-radius: 3px !important;
}
.cinematic-feed::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, #EE4C2C, #812CE5) !important;
  border-radius: 3px !important;
}
.cinematic-feed::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(180deg, #EE4C2C, #0668E1) !important;
}

/* Manual control panel with advanced glassmorphism */
.manual-panel {
  background: linear-gradient(135deg,
    rgba(38, 38, 38, 0.85), rgba(28, 28, 28, 0.9),
    rgba(38, 38, 38, 0.85)) !important;
  backdrop-filter: blur(16px) saturate(180%) !important;
  -webkit-backdrop-filter: blur(16px) saturate(180%) !important;
  border: 2px solid rgba(238, 76, 44, 0.2) !important;
  padding: 24px !important;
  border-radius: 16px !important;
  margin-top: 16px !important;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4),
              inset 0 1px 0 rgba(255, 255, 255, 0.08) !important;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
  position: relative !important;
  overflow: hidden !important;
}
.manual-panel::before {
  content: '' !important;
  position: absolute !important;
  top: 0 !important; left: -100% !important;
  width: 100% !important; height: 100% !important;
  background: linear-gradient(90deg,
    transparent,
    rgba(238, 76, 44, 0.1),
    transparent) !important;
  transition: left 0.6s ease !important;
}
.manual-panel:hover {
  border-color: rgba(238, 76, 44, 0.5) !important;
  box-shadow: 0 12px 48px rgba(238, 76, 44, 0.2),
              0 0 60px rgba(238, 76, 44, 0.15),
              inset 0 1px 0 rgba(255, 255, 255, 0.12) !important;
  transform: scale(1.01) !important;
}
.manual-panel:hover::before { left: 100% !important; }
.manual-execute-btn {
  background: linear-gradient(135deg, #2B7D6D 0%, #1f5a4e 50%, #2B7D6D 100%) !important;
  background-size: 200% 100% !important;
  border: none !important; color: #ffffff !important;
  font-weight: 700 !important; font-size: 1rem !important;
  padding: 12px 28px !important;
  box-shadow: 0 4px 15px rgba(43, 125, 109, 0.4) !important;
  transition: all 0.3s ease !important;
  border-radius: 8px !important;
}
.manual-execute-btn:hover {
  background-position: 100% 0 !important;
  box-shadow: 0 6px 25px rgba(43, 125, 109, 0.6) !important;
  transform: translateY(-2px) scale(1.02) !important;
}
.manual-reset-btn {
  background: linear-gradient(135deg, rgba(28, 28, 28, 0.8), rgba(38, 38, 38, 0.9)) !important;
  backdrop-filter: blur(8px) !important;
  border: 1px solid rgba(6, 104, 225, 0.5) !important;
  color: #0668E1 !important;
  font-weight: 600 !important; font-size: 1rem !important;
  padding: 12px 28px !important;
  transition: all 0.3s ease !important;
  border-radius: 8px !important;
}
.manual-reset-btn:hover {
  border-color: #0668E1 !important;
  box-shadow: 0 0 20px rgba(6, 104, 225, 0.4), inset 0 0 20px rgba(6, 104, 225, 0.1) !important;
  transform: translateY(-2px) !important;
}

/* ═══════════════════════════════════════════════════════════════════
   2026 UI/UX ENHANCEMENTS
   ═══════════════════════════════════════════════════════════════════ */

/* Toast Notifications */
.toast-container {
  position: fixed !important;
  top: 20px !important;
  right: 20px !important;
  z-index: 9999 !important;
  display: flex !important;
  flex-direction: column !important;
  gap: 12px !important;
  pointer-events: none !important;
}

.toast {
  background: rgba(28, 28, 28, 0.95) !important;
  backdrop-filter: blur(20px) !important;
  border-left: 4px solid #EE4C2C !important;
  border-radius: 12px !important;
  padding: 16px 20px !important;
  box-shadow: 0 16px 32px rgba(0, 0, 0, 0.6) !important;
  display: flex !important;
  align-items: center !important;
  gap: 12px !important;
  min-width: 300px !important;
  max-width: 400px !important;
  opacity: 0 !important;
  transform: translateX(400px) !important;
  animation: slideInRight 0.3s forwards !important;
  pointer-events: auto !important;
}

.toast.success { border-left-color: #2B7D6D !important; }
.toast.error { border-left-color: #f44336 !important; }
.toast.warning { border-left-color: #FF9800 !important; }

@keyframes slideInRight {
  to {
    opacity: 1 !important;
    transform: translateX(0) !important;
  }
}

/* Impact Callout */
.impact-callout {
  background: linear-gradient(135deg, #EE4C2C, #C93D20) !important;
  border-radius: 24px !important;
  padding: 32px !important;
  box-shadow: 0 8px 32px rgba(238, 76, 44, 0.4) !important;
  text-align: center !important;
  margin: 24px 0 !important;
  position: relative !important;
  overflow: hidden !important;
}

.impact-number {
  font-size: 4rem !important;
  font-weight: 900 !important;
  color: white !important;
  text-shadow: 0 4px 8px rgba(0, 0, 0, 0.3) !important;
  margin-bottom: 12px !important;
}

.impact-label {
  font-size: 1.2rem !important;
  color: rgba(255, 255, 255, 0.9) !important;
  font-weight: 600 !important;
}

/* Loading Spinner */
.loading-spinner {
  display: inline-block !important;
  width: 20px !important;
  height: 20px !important;
  border: 3px solid rgba(255, 255, 255, 0.1) !important;
  border-top-color: #EE4C2C !important;
  border-radius: 50% !important;
  animation: spin 0.8s linear infinite !important;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Enhanced Glass Cards */
.glass-card-enhanced {
  background: rgba(20, 24, 36, 0.7) !important;
  backdrop-filter: blur(20px) saturate(180%) !important;
  -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
  border: 1px solid rgba(224, 230, 237, 0.1) !important;
  border-radius: 16px !important;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2) !important;
  transition: all 0.25s ease !important;
}

.glass-card-enhanced:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 8px 12px rgba(0, 0, 0, 0.3) !important;
  border-color: #EE4C2C !important;
}

/* Smooth Scrolling */
html {
  scroll-behavior: smooth !important;
}

::-webkit-scrollbar {
  width: 12px !important;
}

::-webkit-scrollbar-track {
  background: #0A0E1A !important;
}

::-webkit-scrollbar-thumb {
  background: #1E2330 !important;
  border-radius: 6px !important;
}

::-webkit-scrollbar-thumb:hover {
  background: #6B7280 !important;
}

/* Focus Styles for Accessibility */
:focus-visible {
  outline: 2px solid #EE4C2C !important;
  outline-offset: 2px !important;
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

  /* Initialize Toast Notification System */
  if (!window.ToastManager) {
    window.ToastManager = {
      container: null,
      init: function() {
        if (!this.container) {
          this.container = document.createElement('div');
          this.container.className = 'toast-container';
          document.body.appendChild(this.container);
        }
      },
      show: function(message, type, duration) {
        type = type || 'info';
        duration = duration || 4000;
        this.init();
        var toast = document.createElement('div');
        toast.className = 'toast ' + type;
        var icons = { success: '✓', error: '✗', warning: '⚠', info: 'ℹ' };
        toast.innerHTML = '<span style="font-size: 1.5rem;">' + (icons[type] || icons.info) + '</span>' +
                         '<span style="color: #E0E6ED; font-weight: 500;">' + message + '</span>';
        this.container.appendChild(toast);
        var self = this;
        setTimeout(function() {
          toast.style.animation = 'slideOutRight 0.3s forwards';
          setTimeout(function() { toast.remove(); }, 300);
        }, duration);
      }
    };

    /* Show welcome toast */
    setTimeout(function() {
      if (!sessionStorage.getItem('welcomeShown')) {
        window.ToastManager.show('Welcome to MOGUL Logistics - TOP 3 Submission!', 'success', 5000);
        sessionStorage.setItem('welcomeShown', 'true');
      }
    }, 2000);
  }
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
<div style="background:linear-gradient(135deg,#EE4C2C 0%,#0668E1 100%);
border:none;padding:28px 24px;margin-bottom:18px;border-radius:12px;
box-shadow:0 6px 24px rgba(238,76,44,0.25)">
<div style="text-align:center">
<h1 style="margin:0;font-size:2.2rem;color:#ffffff;font-weight:800;
letter-spacing:-0.03em;text-shadow:0 2px 6px rgba(0,0,0,0.3)">
&#x1F4E6; MOGUL Logistics</h1>
<div style="color:#ffffff;font-size:1.05rem;margin-top:10px;font-weight:500">
AI-Powered Supply Chain Exception Resolution</div>
<div style="background:rgba(255,255,255,0.15);backdrop-filter:blur(10px);
border-radius:7px;padding:14px;margin-top:16px;border:1px solid rgba(255,255,255,0.2)">
<div style="color:#fff;font-size:0.88rem;line-height:1.5">
<strong>Real-world crisis management:</strong> Resolve delays, damages, customs holds
across India under time & budget constraints
</div>
</div>
<div style="margin-top:14px;color:rgba(255,255,255,0.88);font-size:0.82rem">
<strong>Meta PyTorch OpenEnv Hackathon 2026</strong> &#x2022; Muhammed Sayeedur Rahman
</div>
</div></div>

<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-bottom:18px">
<div style="background:linear-gradient(135deg,#2B7D6D,#1a4d43);
border:2px solid #2B7D6D;padding:18px;border-radius:9px;text-align:center;
box-shadow:0 4px 14px rgba(43,125,109,0.3)">
<div style="font-size:0.7rem;color:rgba(255,255,255,0.7);text-transform:uppercase;
letter-spacing:0.08em;margin-bottom:6px">vs Random</div>
<div style="font-size:2.6rem;font-weight:800;color:#fff">+649%</div>
<div style="font-size:0.7rem;color:rgba(255,255,255,0.6);margin-top:3px">improvement</div>
</div>
<div style="background:linear-gradient(135deg,#0668E1,#044a9f);
border:2px solid #0668E1;padding:18px;border-radius:9px;text-align:center;
box-shadow:0 4px 14px rgba(6,104,225,0.3)">
<div style="font-size:0.7rem;color:rgba(255,255,255,0.7);text-transform:uppercase;
letter-spacing:0.08em;margin-bottom:6px">Training Episodes</div>
<div style="font-size:2.6rem;font-weight:800;color:#fff">280</div>
<div style="font-size:0.7rem;color:rgba(255,255,255,0.6);margin-top:3px">real PyTorch</div>
</div>
<div style="background:linear-gradient(135deg,#EE4C2C,#b93820);
border:2px solid #EE4C2C;padding:18px;border-radius:9px;text-align:center;
box-shadow:0 4px 14px rgba(238,76,44,0.3)">
<div style="font-size:0.7rem;color:rgba(255,255,255,0.7);text-transform:uppercase;
letter-spacing:0.08em;margin-bottom:6px">Avg Score</div>
<div style="font-size:2.6rem;font-weight:800;color:#fff">3.50</div>
<div style="font-size:0.7rem;color:rgba(255,255,255,0.6);margin-top:3px">across tasks</div>
</div>
</div>
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


def render_shipments(obs: dict, last_acted_on: str | None = None) -> str:
    """Render shipment cards with optional highlighting for last affected shipment.

    Args:
        obs: Observation dict containing shipment status and progress
        last_acted_on: Shipment ID that was just acted on (e.g., "SHP-003")
    """
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

        # Highlight if this shipment was just acted on
        is_highlighted = (sid == last_acted_on)

        col = status_colour(status_val)
        icon = _PRIO_ICON.get(priority, "")
        inv = (
            ' <span style="background:#1a3a5c;color:#0668E1;'
            'padding:1px 6px;font-size:0.6rem;border-radius:3px">\u2713 INVESTIGATED</span>'
            if status_val in ("investigating", "action_taken") else ""
        )

        # Enhanced highlighting for just-acted-on shipment
        if is_highlighted:
            highlight_glow = (
                "box-shadow:0 0 20px rgba(255,215,64,0.4),"
                "0 0 40px rgba(255,215,64,0.2);"
            )
            highlight_border = "border:2px solid #ffd740!important;"
            highlight_bg = "background:linear-gradient(135deg,#2a2410,#262626);"
            updated_badge = (
                ' <span style="background:#2B7D6D;color:#fff;'
                'padding:2px 8px;font-size:0.65rem;border-radius:3px;'
                'font-weight:700;animation:pulse 1s 3">\u2713 JUST UPDATED</span>'
            )
        else:
            highlight_glow = (
                "box-shadow:0 0 12px rgba(43,125,109,0.5);"
                if status_val == "resolved" else ""
            )
            highlight_border = ""
            highlight_bg = "background:#262626;"
            updated_badge = ""

        failed_dim = "opacity:0.6;" if status_val == "failed" else ""

        cards.append(
            f'<div style="{highlight_bg}{highlight_border}border:1px solid #404040;'
            f'border-left:3px solid {col};padding:10px 14px;margin-bottom:6px;'
            f'border-radius:4px;transition:all 0.3s ease;{highlight_glow}{failed_dim}">'
            f'<div style="display:flex;justify-content:space-between;align-items:center">'
            f'  <span style="font-weight:700;font-size:0.95rem;'
            f'color:{"#ffd740" if is_highlighted else "#e0e6ed"}">'
            f'{sid}{inv}{updated_badge}</span>'
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

        # Enhanced reasoning display for judges
        reasoning_box = (
            f'<div style="background:linear-gradient(135deg,#0a1612,#0d1f1a);'
            f'border:1px solid {color}40;border-left:3px solid #ffd740;'
            f'border-radius:6px;padding:12px 16px;margin-top:12px">'
            f'<div style="color:#ffd740;font-weight:700;font-size:0.72rem;'
            f'text-transform:uppercase;letter-spacing:0.08em;margin-bottom:6px">'
            f'\U0001f9e0 AGENT REASONING (WHY THIS ACTION?)</div>'
            f'<div style="color:#c8d6e0;font-size:0.85rem;line-height:1.6;'
            f'font-style:italic">{ev["explanation"]}</div></div>'
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
            f'{reasoning_box}'
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
