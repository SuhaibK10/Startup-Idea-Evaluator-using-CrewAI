"""
VentureScope — AI-Powered Startup Idea Evaluator
Five specialized CrewAI agents evaluate your idea with the rigor of a top-tier VC fund.
"""

from __future__ import annotations

import os
import datetime
from dotenv import load_dotenv

import streamlit as st
from crewai import LLM

from agents import (
    problem_validator,
    market_researcher,
    business_model_builder,
    risk_analyst,
    vc_memo_writer,
)
from tasks import (
    make_validate_task,
    make_research_task,
    make_bizmodel_task,
    make_risk_task,
    make_memo_task,
)
from scoring import parse_scores, overall_score, verdict, radar_chart
from pdf_export import generate_pdf

load_dotenv()

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="VentureScope — AI Startup Evaluator",
    page_icon="🔭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

html, body, [class*="css"], .stMarkdown p, .stMarkdown li {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}
#MainMenu, footer, .stDeployButton { visibility: hidden; }
.block-container { padding: 1.25rem 2rem 4rem 2rem; max-width: 1200px; }

/* ── Hero ── */
.vs-hero {
    background: linear-gradient(135deg, #080f1e 0%, #0e2350 50%, #0c3070 100%);
    padding: 2.5rem 3rem 2rem 3rem;
    border-radius: 22px;
    margin-bottom: 1.75rem;
    position: relative;
    overflow: hidden;
}
.vs-hero::before {
    content: '';
    position: absolute;
    top: -80px; right: -80px;
    width: 320px; height: 320px;
    background: radial-gradient(circle, rgba(99,179,237,.18) 0%, transparent 68%);
    border-radius: 50%;
    pointer-events: none;
}
.vs-hero::after {
    content: '';
    position: absolute;
    bottom: -60px; left: 40%;
    width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(167,139,250,.1) 0%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
}
.vs-tag {
    display: inline-block;
    background: rgba(255,255,255,.08);
    border: 1px solid rgba(255,255,255,.12);
    color: #93c5fd;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 2px;
    text-transform: uppercase;
    padding: 4px 14px;
    border-radius: 20px;
    margin-bottom: 1rem;
}
.vs-hero h1 {
    font-size: 2.5rem;
    font-weight: 900;
    color: #ffffff;
    margin: 0 0 0.4rem 0;
    letter-spacing: -1px;
    line-height: 1.15;
}
.vs-hero p {
    color: #93c5fd;
    font-size: 1rem;
    margin: 0;
    font-weight: 400;
    max-width: 540px;
}

/* ── Score card ── */
.score-card {
    background: #ffffff;
    border-radius: 18px;
    padding: 2rem 2.5rem;
    box-shadow: 0 4px 30px rgba(0,0,0,.07);
    border: 1px solid #e8ecf4;
    height: 100%;
}
.big-score {
    font-size: 5.5rem;
    font-weight: 900;
    line-height: 1;
    letter-spacing: -4px;
}
.score-subtitle {
    font-size: 0.78rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: #94a3b8;
    margin-bottom: 0.4rem;
}
.verdict-badge {
    display: inline-block;
    padding: 6px 20px;
    border-radius: 24px;
    font-size: 0.82rem;
    font-weight: 700;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    margin-top: 0.75rem;
}
.dim-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 0.6rem;
    margin-top: 1.5rem;
}
.dim-cell {
    background: #f8fafc;
    border-radius: 10px;
    padding: 0.65rem 0.5rem;
    text-align: center;
    border: 1px solid #e2e8f0;
}
.dim-val { font-size: 1.5rem; font-weight: 800; color: #0f172a; }
.dim-lbl { font-size: 0.63rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; color: #64748b; margin-top: 2px; }

/* ── Feature cards (landing) ── */
.feat-card {
    background: #ffffff;
    border-radius: 14px;
    padding: 1.5rem;
    border: 1px solid #e8ecf4;
    box-shadow: 0 2px 12px rgba(0,0,0,.04);
    height: 100%;
}
.feat-icon { font-size: 1.6rem; margin-bottom: 0.6rem; }
.feat-title { font-size: 0.9rem; font-weight: 700; color: #0f172a; margin-bottom: 0.3rem; }
.feat-desc { font-size: 0.82rem; color: #64748b; line-height: 1.5; }

/* ── Section divider label ── */
.section-label {
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: #94a3b8;
    margin: 2rem 0 0.75rem 0;
    display: flex;
    align-items: center;
    gap: 0.75rem;
}
.section-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: #e2e8f0;
}

/* ── Investment memo highlight ── */
.memo-wrap {
    background: linear-gradient(135deg, #f0f7ff 0%, #f5f0ff 100%);
    border: 1.5px solid #c7d7f5;
    border-radius: 18px;
    padding: 2.5rem 3rem;
    box-shadow: 0 4px 24px rgba(26,74,138,.08);
}

/* ── Progress steps ── */
.step-done   { padding: 0.5rem 1rem; background: #f0fdf4; color: #15803d;
               border-radius: 8px; font-size: 0.9rem; margin: 0.25rem 0; }
.step-active { padding: 0.5rem 1rem; background: #eff6ff; color: #1d4ed8;
               border-radius: 8px; font-size: 0.9rem; margin: 0.25rem 0; }
.step-wait   { padding: 0.5rem 1rem; background: #f8fafc; color: #94a3b8;
               border-radius: 8px; font-size: 0.9rem; margin: 0.25rem 0; }

/* ── Sidebar ── */
[data-testid="stSidebar"] { background: #f8fafc; }
[data-testid="stSidebar"] .stTextInput > div > div { border-radius: 8px; }
[data-testid="stSidebar"] .stTextArea  > div > div { border-radius: 8px; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────

def textify(x) -> str:
    if hasattr(x, "raw") and isinstance(x.raw, str):
        return x.raw
    for attr in ("output", "final_output", "text", "content"):
        val = getattr(x, attr, None)
        if isinstance(val, str):
            return val
    if isinstance(x, (list, tuple)):
        return "\n\n".join(textify(i) for i in x)
    return str(x) if x is not None else ""


def join_ctx(*parts) -> str:
    return "\n\n---\n\n".join(textify(p) for p in parts if p)


def make_llm() -> LLM:
    return LLM(
        model=os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini"),
        base_url=os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1"),
        api_key=os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY"),
        temperature=0.2,
    )


# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="vs-hero">
    <div class="vs-tag">⚡ 5-Agent CrewAI System &nbsp;·&nbsp; VC-Grade Analysis</div>
    <h1>VentureScope</h1>
    <p>Five specialized AI agents evaluate your startup idea with the rigor and frameworks
    used by top-tier venture capital funds.</p>
</div>
""", unsafe_allow_html=True)


# ── Sidebar inputs ────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## Your Startup Idea")
    st.caption("The more detail you provide, the sharper the analysis.")

    idea = st.text_area(
        "Describe the idea \\*",
        height=150,
        placeholder=(
            "e.g., AI voice bot for dermatology clinics to auto-book appointments, "
            "handle insurance pre-auth queries, and send post-visit follow-ups — "
            "cutting front-desk workload by 60-70%."
        ),
    )

    st.divider()
    st.markdown("**Market Details**")
    c1, c2 = st.columns(2)
    with c1:
        target = st.text_input("Target Customer", placeholder="e.g., dermatology clinics")
    with c2:
        region = st.text_input("Region / Market", placeholder="e.g., India")
    price = st.text_input("Intended Pricing", placeholder="e.g., ₹2,999/month")

    st.divider()
    st.markdown("**Optional Context**")
    team     = st.text_input("Team Background",   placeholder="e.g., ex-Amazon PM + IIT ML engineer")
    traction = st.text_input("Current Traction",  placeholder="e.g., 3 pilot clinics, 200 bookings")

    st.divider()
    run_btn = st.button("🔭 Run VC-Grade Evaluation", type="primary", use_container_width=True)


# ── Run analysis ──────────────────────────────────────────────────────────────
if run_btn:
    if not idea.strip():
        st.warning("Please describe your startup idea to get started.")
        st.stop()

    problem_ctx = "\n".join([
        f"**Startup Idea**: {idea}",
        f"**Target Customer**: {target  or 'Not specified'}",
        f"**Market / Region**: {region  or 'Not specified'}",
        f"**Intended Pricing**: {price  or 'Not specified'}",
        f"**Team Background**: {team    or 'Not specified'}",
        f"**Current Traction**: {traction or 'None yet'}",
    ])

    llm = make_llm()

    validator = problem_validator(llm)
    researcher = market_researcher(llm)
    modeler   = business_model_builder(llm)
    risker    = risk_analyst(llm)
    writer    = vc_memo_writer(llm)

    outputs: dict[str, str] = {}

    STEPS = [
        ("🔍", "Problem Validator",      "Analyzing problem-solution fit…"),
        ("📊", "Market Researcher",      "Sizing the market & mapping competitors…"),
        ("💼", "Business Strategist",    "Designing unit economics & GTM plan…"),
        ("⚠️",  "Risk & Moat Analyst",   "Stress-testing risks & defensibility…"),
        ("📄", "VC Memo Writer",         "Writing investment committee memo…"),
    ]

    prog_slot = st.empty()

    def _render_steps(done: set[int], active: int | None) -> None:
        html = '<div style="margin:0.5rem 0 1.5rem 0">'
        for i, (icon, name, desc) in enumerate(STEPS):
            if i in done:
                html += f'<div class="step-done">✅ {icon} {name}</div>'
            elif i == active:
                html += f'<div class="step-active">⏳ {icon} {name} — {desc}</div>'
            else:
                html += f'<div class="step-wait">○ {icon} {name}</div>'
        html += "</div>"
        prog_slot.markdown(html, unsafe_allow_html=True)

    done: set[int] = set()
    _render_steps(done, 0)

    # ── Agent 1 ───────────────────────────────────────────────────────────────
    t = make_validate_task(validator, problem_ctx)
    outputs["validate"] = textify(t.execute_sync(agent=validator, context=None, tools=[]))
    done.add(0); _render_steps(done, 1)

    # ── Agent 2 ───────────────────────────────────────────────────────────────
    t = make_research_task(researcher, problem_ctx, outputs["validate"])
    outputs["research"] = textify(t.execute_sync(agent=researcher, context=outputs["validate"], tools=[]))
    done.add(1); _render_steps(done, 2)

    # ── Agent 3 ───────────────────────────────────────────────────────────────
    prior_bm = join_ctx(outputs["validate"], outputs["research"])
    t = make_bizmodel_task(modeler, problem_ctx, prior_bm)
    outputs["bizmodel"] = textify(t.execute_sync(agent=modeler, context=prior_bm, tools=[]))
    done.add(2); _render_steps(done, 3)

    # ── Agent 4 ───────────────────────────────────────────────────────────────
    prior_risk = join_ctx(outputs["validate"], outputs["research"], outputs["bizmodel"])
    t = make_risk_task(risker, problem_ctx, prior_risk)
    outputs["risks"] = textify(t.execute_sync(agent=risker, context=prior_risk, tools=[]))
    done.add(3); _render_steps(done, 4)

    # ── Agent 5 ───────────────────────────────────────────────────────────────
    prior_memo = join_ctx(outputs["validate"], outputs["research"], outputs["bizmodel"], outputs["risks"])
    t = make_memo_task(writer, problem_ctx, prior_memo)
    outputs["memo"] = textify(t.execute_sync(agent=writer, context=prior_memo, tools=[]))
    done.add(4); _render_steps(done, None)

    prog_slot.empty()

    # ── Scoring ───────────────────────────────────────────────────────────────
    dim = parse_scores(outputs)
    total = overall_score(dim)
    v_label, v_emoji, v_color = verdict(total)

    verdict_css = {
        "Strong Interest": ("badge-strong",    "#dcfce7", "#15803d"),
        "Watchlist":        ("badge-watchlist", "#fef3c7", "#92400e"),
        "Needs Work":       ("badge-needs",     "#ffedd5", "#9a3412"),
        "Pass":             ("badge-pass",      "#fee2e2", "#991b1b"),
    }.get(v_label, ("badge-pass", "#f1f5f9", "#475569"))

    # ── Score card + radar chart ──────────────────────────────────────────────
    col_score, col_chart = st.columns([1, 1.15], gap="large")

    with col_score:
        st.markdown(f"""
        <div class="score-card">
            <div class="score-subtitle">Investment Score</div>
            <div class="big-score" style="color:{v_color}">{total}</div>
            <div style="color:#94a3b8;font-size:1.1rem;margin-top:-4px">/ 100</div>
            <div class="verdict-badge"
                 style="background:{verdict_css[1]};color:{verdict_css[2]}">
                {v_emoji} {v_label}
            </div>
            <div class="dim-grid">
                <div class="dim-cell">
                    <div class="dim-val">{dim.get("problem",0)}</div>
                    <div class="dim-lbl">Problem</div>
                </div>
                <div class="dim-cell">
                    <div class="dim-val">{dim.get("market",0)}</div>
                    <div class="dim-lbl">Market</div>
                </div>
                <div class="dim-cell">
                    <div class="dim-val">{dim.get("biz_model",0)}</div>
                    <div class="dim-lbl">Biz Model</div>
                </div>
                <div class="dim-cell">
                    <div class="dim-val">{dim.get("execution",0)}</div>
                    <div class="dim-lbl">Execution</div>
                </div>
                <div class="dim-cell">
                    <div class="dim-val">{dim.get("moat",0)}</div>
                    <div class="dim-lbl">Moat</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_chart:
        fig = radar_chart(dim)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # ── Detailed Analysis ─────────────────────────────────────────────────────
    st.markdown(
        '<div class="section-label">Detailed Analysis</div>',
        unsafe_allow_html=True,
    )

    with st.expander("🔍  Problem Validator", expanded=False):
        st.markdown(outputs["validate"])

    with st.expander("📊  Market Research", expanded=False):
        st.markdown(outputs["research"])

    with st.expander("💼  Business Model & GTM", expanded=False):
        st.markdown(outputs["bizmodel"])

    with st.expander("⚠️  Risk & Moat Analysis", expanded=False):
        st.markdown(outputs["risks"])

    # ── Investment Memo ───────────────────────────────────────────────────────
    st.markdown(
        '<div class="section-label">VC Investment Memo</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="memo-wrap">', unsafe_allow_html=True)
    st.markdown(outputs["memo"])
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Download ──────────────────────────────────────────────────────────────
    st.divider()
    score_data = {
        "overall_score": total,
        "verdict": f"{v_emoji} {v_label}",
        "dimensions": dim,
    }
    try:
        pdf_bytes = generate_pdf(
            idea, target or "", region or "", score_data, outputs
        )
        st.download_button(
            label="⬇️  Download Full Report (PDF)",
            data=pdf_bytes,
            file_name=f"venturescope_{datetime.date.today()}.pdf",
            mime="application/pdf",
            type="primary",
        )
    except RuntimeError as e:
        st.caption(f"PDF export unavailable: {e}")


# ── Landing state ─────────────────────────────────────────────────────────────
else:
    st.markdown("""
    <div style="text-align:center;padding:3rem 1rem 2rem 1rem">
        <div style="font-size:3.5rem;margin-bottom:0.75rem">🔭</div>
        <div style="font-size:1.25rem;font-weight:700;color:#1e293b;margin-bottom:0.4rem">
            Ready to evaluate your startup idea
        </div>
        <div style="font-size:0.95rem;color:#64748b">
            Describe your idea in the sidebar and click <strong>Run VC-Grade Evaluation</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)

    r1c1, r1c2, r1c3 = st.columns(3, gap="medium")
    r2c1, r2c2, r2c3 = st.columns(3, gap="medium")

    cards = [
        ("🔍", "Problem Validator",
         "Rates pain intensity, frequency, and problem-solution fit using "
         "Jobs-to-be-Done and hair-on-fire frameworks."),
        ("📊", "Market Researcher",
         "Builds a bottom-up TAM/SAM/SOM, maps 4-6 competitors, and finds "
         "the 'why now' timing unlock."),
        ("💼", "Business Strategist",
         "Designs pricing tiers, unit economics (LTV:CAC, payback), and "
         "a concrete 90-day GTM plan."),
        ("⚠️", "Risk & Moat Analyst",
         "Stress-tests 5 risk categories, scores 6 moat types, and lists "
         "the deal-breaker red flags."),
        ("📄", "VC Memo Writer",
         "Produces an IC-ready investment memo with thesis, comps table, "
         "and a preliminary verdict."),
        ("📈", "Investment Score",
         "Weighted 0-100 score across 5 dimensions, visualised as an "
         "interactive radar chart. PDF export included."),
    ]

    for col, (icon, title, desc) in zip(
        [r1c1, r1c2, r1c3, r2c1, r2c2, r2c3], cards
    ):
        col.markdown(f"""
        <div class="feat-card">
            <div class="feat-icon">{icon}</div>
            <div class="feat-title">{title}</div>
            <div class="feat-desc">{desc}</div>
        </div>
        """, unsafe_allow_html=True)
