import re
from typing import Any

import plotly.graph_objects as go


# ── Score extraction ──────────────────────────────────────────────────────────

_PATTERNS: dict[str, tuple[str, str]] = {
    "problem":    (r"PROBLEM_SCORE\s*:\s*(\d+)", "validate"),
    "market":     (r"MARKET_SCORE\s*:\s*(\d+)",  "research"),
    "biz_model":  (r"BIZMODEL_SCORE\s*:\s*(\d+)", "bizmodel"),
    "execution":  (r"RISK_SCORE\s*:\s*(\d+)",     "risks"),
    "moat":       (r"MOAT_SCORE\s*:\s*(\d+)",     "risks"),
}

_WEIGHTS = {
    "problem":   0.25,
    "market":    0.20,
    "biz_model": 0.20,
    "execution": 0.20,
    "moat":      0.15,
}

_LABELS = {
    "problem":   "Problem / Pain",
    "market":    "Market Size",
    "biz_model": "Biz Model",
    "execution": "Execution",
    "moat":      "Moat",
}


def parse_scores(outputs: dict[str, str]) -> dict[str, int]:
    scores: dict[str, int] = {}
    for key, (pattern, src_key) in _PATTERNS.items():
        text = outputs.get(src_key, "")
        m = re.search(pattern, text, re.IGNORECASE)
        raw = int(m.group(1)) if m else 5
        scores[key] = max(1, min(10, raw))
    return scores


def overall_score(dim: dict[str, int]) -> int:
    total = sum(dim.get(k, 5) * w * 10 for k, w in _WEIGHTS.items())
    return max(0, min(100, round(total)))


def verdict(score: int) -> tuple[str, str, str]:
    """Returns (label, emoji, hex_color)."""
    if score >= 75:
        return "Strong Interest", "🟢", "#16a34a"
    if score >= 55:
        return "Watchlist",       "🟡", "#d97706"
    if score >= 35:
        return "Needs Work",      "🟠", "#ea580c"
    return "Pass",                "🔴", "#dc2626"


# ── Plotly radar chart ────────────────────────────────────────────────────────

def radar_chart(dim: dict[str, int]) -> go.Figure:
    keys   = list(_LABELS.keys())
    cats   = [_LABELS[k] for k in keys]
    vals   = [dim.get(k, 0) for k in keys]

    # close the polygon
    cats_c = cats + [cats[0]]
    vals_c = vals + [vals[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=vals_c,
        theta=cats_c,
        fill="toself",
        fillcolor="rgba(26, 74, 138, 0.12)",
        line=dict(color="#1a4a8a", width=2.5),
        marker=dict(size=7, color="#1a4a8a"),
        hovertemplate="%{theta}: <b>%{r}/10</b><extra></extra>",
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10],
                tickvals=[2, 4, 6, 8, 10],
                tickfont=dict(size=9, color="#94a3b8"),
                gridcolor="#e2e8f0",
                linecolor="#e2e8f0",
            ),
            angularaxis=dict(
                tickfont=dict(size=12, color="#1e293b"),
                linecolor="#e2e8f0",
                gridcolor="#e2e8f0",
            ),
            bgcolor="white",
        ),
        showlegend=False,
        paper_bgcolor="white",
        plot_bgcolor="white",
        margin=dict(l=55, r=55, t=30, b=30),
        height=300,
    )
    return fig
