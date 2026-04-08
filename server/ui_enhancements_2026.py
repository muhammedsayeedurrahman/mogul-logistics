"""2026 UI/UX Enhancements for MOGUL Logistics Dashboard.

Inspired by top design websites:
- Awwwards (cutting-edge creativity)
- Godly (animated, motion-rich)
- Mobbin (real product patterns)
- Siteinspire (clean, typography-driven)
- Httpster (minimal restraint)
"""

# ── Color Palette (Modern Logistics 2026) ────────────────────────────
COLORS_2026 = {
    # Primary palette
    "primary": "#EE4C2C",  # PyTorch orange (vibrant, energetic)
    "primary_dark": "#C93D20",
    "primary_light": "#FF6347",

    # Secondary palette
    "secondary": "#0668E1",  # Deep blue (trust, intelligence)
    "secondary_dark": "#0451B5",
    "secondary_light": "#2B7FE8",

    # Accent colors
    "accent_green": "#2B7D6D",  # Success, logistics green
    "accent_gold": "#FFD740",   # Warning, important
    "accent_purple": "#9C27B0",  # Premium features

    # Neutrals (slate-based for sophistication)
    "bg_dark": "#0A0E1A",  # Near-black background
    "bg_mid": "#141824",   # Card background
    "bg_light": "#1E2330", # Elevated surfaces
    "text_primary": "#E0E6ED",  # High contrast white
    "text_secondary": "#A0A8B8",  # Muted text
    "text_tertiary": "#6B7280",  # Subtle text

    # Status colors
    "success": "#4CAF50",
    "warning": "#FF9800",
    "error": "#F44336",
    "info": "#2196F3",

    # Glass morphism
    "glass_bg": "rgba(20, 24, 36, 0.7)",
    "glass_border": "rgba(224, 230, 237, 0.1)",
}


# ── Advanced CSS (2026 Design Trends) ────────────────────────────────
ADVANCED_CSS_2026 = f"""
/* ═══════════════════════════════════════════════════════════════════
   MOGUL LOGISTICS - 2026 UI/UX ENHANCEMENTS
   Inspired by: Awwwards, Godly, Mobbin, Siteinspire, Httpster
   ═══════════════════════════════════════════════════════════════════ */

/* ── Root Variables ────────────────────────────────────────────── */
:root {{
    /* Color palette */
    --color-primary: {COLORS_2026['primary']};
    --color-primary-dark: {COLORS_2026['primary_dark']};
    --color-secondary: {COLORS_2026['secondary']};
    --color-accent-green: {COLORS_2026['accent_green']};
    --color-accent-gold: {COLORS_2026['accent_gold']};

    /* Backgrounds */
    --bg-dark: {COLORS_2026['bg_dark']};
    --bg-mid: {COLORS_2026['bg_mid']};
    --bg-light: {COLORS_2026['bg_light']};

    /* Text */
    --text-primary: {COLORS_2026['text_primary']};
    --text-secondary: {COLORS_2026['text_secondary']};
    --text-tertiary: {COLORS_2026['text_tertiary']};

    /* Glass morphism */
    --glass-bg: {COLORS_2026['glass_bg']};
    --glass-border: {COLORS_2026['glass_border']};

    /* Spacing system (8px base) */
    --space-xs: 0.5rem;
    --space-sm: 1rem;
    --space-md: 1.5rem;
    --space-lg: 2rem;
    --space-xl: 3rem;

    /* Border radius */
    --radius-sm: 6px;
    --radius-md: 12px;
    --radius-lg: 16px;
    --radius-xl: 24px;

    /* Shadows (layered depth) */
    --shadow-sm: 0 2px 4px rgba(0, 0, 0, 0.1);
    --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.2);
    --shadow-lg: 0 8px 12px rgba(0, 0, 0, 0.3);
    --shadow-xl: 0 16px 24px rgba(0, 0, 0, 0.4);

    /* Animations */
    --transition-fast: 150ms ease;
    --transition-normal: 250ms ease;
    --transition-slow: 400ms ease;
}}

/* ── Glass Morphism Cards ──────────────────────────────────────── */
.glass-card {{
    background: var(--glass-bg);
    backdrop-filter: blur(20px) saturate(180%);
    -webkit-backdrop-filter: blur(20px) saturate(180%);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-md);
    transition: all var(--transition-normal);
}}

.glass-card:hover {{
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg);
    border-color: var(--color-primary);
}}

/* ── Toast Notifications ───────────────────────────────────────── */
.toast-container {{
    position: fixed;
    top: var(--space-md);
    right: var(--space-md);
    z-index: 9999;
    display: flex;
    flex-direction: column;
    gap: var(--space-sm);
    pointer-events: none;
}}

.toast {{
    background: var(--bg-mid);
    border-left: 4px solid var(--color-primary);
    border-radius: var(--radius-md);
    padding: var(--space-sm) var(--space-md);
    box-shadow: var(--shadow-xl);
    display: flex;
    align-items: center;
    gap: var(--space-sm);
    min-width: 300px;
    max-width: 400px;
    opacity: 0;
    transform: translateX(400px);
    animation: slideInRight var(--transition-normal) forwards;
    pointer-events: auto;
}}

.toast.success {{
    border-left-color: var(--color-accent-green);
}}

.toast.error {{
    border-left-color: {COLORS_2026['error']};
}}

.toast.warning {{
    border-left-color: {COLORS_2026['warning']};
}}

@keyframes slideInRight {{
    to {{
        opacity: 1;
        transform: translateX(0);
    }}
}}

@keyframes slideOutRight {{
    to {{
        opacity: 0;
        transform: translateX(400px);
    }}
}}

.toast.exit {{
    animation: slideOutRight var(--transition-normal) forwards;
}}

/* ── Interactive Tooltips ──────────────────────────────────────── */
.tooltip-wrapper {{
    position: relative;
    display: inline-block;
}}

.tooltip {{
    position: absolute;
    bottom: calc(100% + var(--space-xs));
    left: 50%;
    transform: translateX(-50%);
    background: var(--bg-dark);
    color: var(--text-primary);
    padding: var(--space-xs) var(--space-sm);
    border-radius: var(--radius-sm);
    font-size: 0.875rem;
    white-space: nowrap;
    box-shadow: var(--shadow-md);
    opacity: 0;
    pointer-events: none;
    transition: opacity var(--transition-fast);
    z-index: 100;
}}

.tooltip::after {{
    content: '';
    position: absolute;
    top: 100%;
    left: 50%;
    transform: translateX(-50%);
    border: 6px solid transparent;
    border-top-color: var(--bg-dark);
}}

.tooltip-wrapper:hover .tooltip {{
    opacity: 1;
}}

/* ── Guided Tour Overlay ───────────────────────────────────────── */
.tour-overlay {{
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.8);
    z-index: 9998;
    display: none;
}}

.tour-overlay.active {{
    display: block;
}}

.tour-spotlight {{
    position: absolute;
    border: 3px solid var(--color-primary);
    border-radius: var(--radius-md);
    box-shadow: 0 0 0 9999px rgba(0, 0, 0, 0.8);
    transition: all var(--transition-normal);
    z-index: 9999;
}}

.tour-popup {{
    position: absolute;
    background: var(--bg-mid);
    border: 1px solid var(--color-primary);
    border-radius: var(--radius-lg);
    padding: var(--space-md);
    max-width: 350px;
    box-shadow: var(--shadow-xl);
    z-index: 10000;
}}

.tour-popup h3 {{
    color: var(--color-primary);
    font-size: 1.25rem;
    margin-bottom: var(--space-sm);
}}

.tour-popup p {{
    color: var(--text-secondary);
    font-size: 0.95rem;
    line-height: 1.6;
    margin-bottom: var(--space-md);
}}

.tour-buttons {{
    display: flex;
    gap: var(--space-sm);
    justify-content: flex-end;
}}

.tour-btn {{
    padding: var(--space-xs) var(--space-md);
    border-radius: var(--radius-sm);
    font-size: 0.9rem;
    font-weight: 600;
    cursor: pointer;
    transition: all var(--transition-fast);
    border: none;
}}

.tour-btn.primary {{
    background: var(--color-primary);
    color: white;
}}

.tour-btn.primary:hover {{
    background: var(--color-primary-dark);
    transform: translateY(-1px);
}}

.tour-btn.secondary {{
    background: transparent;
    color: var(--text-secondary);
    border: 1px solid var(--glass-border);
}}

.tour-btn.secondary:hover {{
    background: var(--bg-light);
}}

/* ── Loading Animations ────────────────────────────────────────── */
.loading-spinner {{
    display: inline-block;
    width: 20px;
    height: 20px;
    border: 3px solid var(--glass-border);
    border-top-color: var(--color-primary);
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
}}

@keyframes spin {{
    to {{ transform: rotate(360deg); }}
}}

.loading-pulse {{
    display: inline-block;
    width: 12px;
    height: 12px;
    background: var(--color-primary);
    border-radius: 50%;
    animation: pulse 1.5s ease-in-out infinite;
}}

@keyframes pulse {{
    0%, 100% {{ opacity: 1; transform: scale(1); }}
    50% {{ opacity: 0.4; transform: scale(0.8); }}
}}

/* ── Impact Callout Box ────────────────────────────────────────── */
.impact-callout {{
    background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
    border-radius: var(--radius-xl);
    padding: var(--space-lg);
    box-shadow: 0 8px 32px rgba(238, 76, 44, 0.3);
    text-align: center;
    margin: var(--space-lg) 0;
    position: relative;
    overflow: hidden;
}}

.impact-callout::before {{
    content: '';
    position: absolute;
    top: -50%;
    right: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
    animation: rotate 20s linear infinite;
}}

@keyframes rotate {{
    from {{ transform: rotate(0deg); }}
    to {{ transform: rotate(360deg); }}
}}

.impact-number {{
    font-size: 4rem;
    font-weight: 900;
    color: white;
    text-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
    margin-bottom: var(--space-sm);
    position: relative;
    z-index: 1;
}}

.impact-label {{
    font-size: 1.2rem;
    color: rgba(255, 255, 255, 0.9);
    font-weight: 600;
    position: relative;
    z-index: 1;
}}

/* ── Responsive Design ─────────────────────────────────────────── */
@media (max-width: 768px) {{
    :root {{
        --space-lg: 1.5rem;
        --space-xl: 2rem;
    }}

    .glass-card {{
        border-radius: var(--radius-md);
    }}

    .toast {{
        min-width: 250px;
    }}

    .tour-popup {{
        max-width: 90vw;
    }}

    .impact-number {{
        font-size: 3rem;
    }}
}}

/* ── Accessibility Enhancements ────────────────────────────────── */
.sr-only {{
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border: 0;
}}

:focus-visible {{
    outline: 2px solid var(--color-primary);
    outline-offset: 2px;
}}

/* Ensure sufficient contrast */
.text-primary {{
    color: var(--text-primary);
}}

.text-secondary {{
    color: var(--text-secondary);
}}

/* ── Smooth Scrolling ──────────────────────────────────────────── */
html {{
    scroll-behavior: smooth;
}}

/* Custom scrollbar */
::-webkit-scrollbar {{
    width: 12px;
}}

::-webkit-scrollbar-track {{
    background: var(--bg-dark);
}}

::-webkit-scrollbar-thumb {{
    background: var(--bg-light);
    border-radius: var(--radius-sm);
}}

::-webkit-scrollbar-thumb:hover {{
    background: var(--text-tertiary);
}}
"""


# ── Toast Notification JavaScript ─────────────────────────────────
TOAST_JS = """
<script>
// Toast Notification System
const ToastManager = {
    container: null,

    init() {
        if (!this.container) {
            this.container = document.createElement('div');
            this.container.className = 'toast-container';
            document.body.appendChild(this.container);
        }
    },

    show(message, type = 'info', duration = 4000) {
        this.init();

        const toast = document.createElement('div');
        toast.className = `toast ${type}`;

        const icons = {
            success: '✓',
            error: '✗',
            warning: '⚠',
            info: 'ℹ'
        };

        toast.innerHTML = `
            <span style="font-size: 1.5rem;">${icons[type] || icons.info}</span>
            <span style="color: var(--text-primary); font-weight: 500;">${message}</span>
        `;

        this.container.appendChild(toast);

        setTimeout(() => {
            toast.classList.add('exit');
            setTimeout(() => toast.remove(), 300);
        }, duration);
    }
};

// Auto-show toasts for actions
document.addEventListener('DOMContentLoaded', () => {
    // Show welcome toast on first load
    if (!sessionStorage.getItem('welcomeShown')) {
        ToastManager.show('Welcome to MOGUL Logistics! 🚛', 'success', 5000);
        sessionStorage.setItem('welcomeShown', 'true');
    }
});
</script>
"""


# ── Guided Tour JavaScript ─────────────────────────────────────────
GUIDED_TOUR_JS = """
<script>
// Guided Tour System
const GuidedTour = {
    steps: [
        {
            element: '#difficulty-selector',
            title: '1. Select Difficulty',
            description: 'Choose Easy (1 shipment), Medium (4 shipments), or Hard (8 shipments) to see different challenges.',
            position: 'bottom'
        },
        {
            element: '#run-demo-btn',
            title: '2. Run AI Demo',
            description: 'Click here to watch the AI agent solve shipments automatically with strategic decision-making.',
            position: 'bottom'
        },
        {
            element: '#constraints-panel',
            title: '3. Live Constraints',
            description: 'Monitor real-time budget, time, and SLA constraints with predictive forecasting.',
            position: 'left'
        },
        {
            element: '#negotiation-panel',
            title: '4. Multi-Agent Negotiation',
            description: 'See three AI agents (Carrier, Customs, Warehouse) negotiate to reach consensus.',
            position: 'left'
        },
        {
            element: '#explainable-ai-panel',
            title: '5. Explainable AI',
            description: 'Understand exactly why each decision was made with full transparency.',
            position: 'left'
        }
    ],
    currentStep: 0,
    overlay: null,
    spotlight: null,
    popup: null,

    init() {
        // Create overlay
        this.overlay = document.createElement('div');
        this.overlay.className = 'tour-overlay';
        document.body.appendChild(this.overlay);

        // Create spotlight
        this.spotlight = document.createElement('div');
        this.spotlight.className = 'tour-spotlight';
        document.body.appendChild(this.spotlight);

        // Create popup
        this.popup = document.createElement('div');
        this.popup.className = 'tour-popup';
        document.body.appendChild(this.popup);
    },

    start() {
        if (!this.overlay) this.init();
        this.currentStep = 0;
        this.showStep();
    },

    showStep() {
        if (this.currentStep >= this.steps.length) {
            this.end();
            return;
        }

        const step = this.steps[this.currentStep];
        const element = document.querySelector(step.element);

        if (!element) {
            // Skip missing elements
            this.currentStep++;
            this.showStep();
            return;
        }

        // Show overlay
        this.overlay.classList.add('active');

        // Position spotlight
        const rect = element.getBoundingClientRect();
        this.spotlight.style.top = `${rect.top - 10}px`;
        this.spotlight.style.left = `${rect.left - 10}px`;
        this.spotlight.style.width = `${rect.width + 20}px`;
        this.spotlight.style.height = `${rect.height + 20}px`;

        // Position popup
        this.popup.innerHTML = `
            <h3>${step.title}</h3>
            <p>${step.description}</p>
            <div class="tour-buttons">
                <button class="tour-btn secondary" onclick="GuidedTour.skip()">Skip</button>
                <button class="tour-btn primary" onclick="GuidedTour.next()">
                    ${this.currentStep < this.steps.length - 1 ? 'Next' : 'Finish'}
                </button>
            </div>
        `;

        // Position popup relative to element
        this.popup.style.top = `${rect.bottom + 20}px`;
        this.popup.style.left = `${Math.max(20, rect.left)}px`;
    },

    next() {
        this.currentStep++;
        this.showStep();
    },

    skip() {
        this.end();
    },

    end() {
        this.overlay.classList.remove('active');
        ToastManager.show('Tour complete! Enjoy exploring MOGUL Logistics.', 'success');
    }
};

// Auto-start tour button
document.addEventListener('DOMContentLoaded', () => {
    // Add tour start button to sidebar (if not exists)
    setTimeout(() => {
        const sidebar = document.querySelector('.sidebar');
        if (sidebar && !document.getElementById('tour-start-btn')) {
            const tourBtn = document.createElement('button');
            tourBtn.id = 'tour-start-btn';
            tourBtn.className = 'tour-btn primary';
            tourBtn.innerText = '🎓 Start Guided Tour';
            tourBtn.style.marginTop = '1rem';
            tourBtn.onclick = () => GuidedTour.start();
            sidebar.appendChild(tourBtn);
        }
    }, 1000);
});
</script>
"""
