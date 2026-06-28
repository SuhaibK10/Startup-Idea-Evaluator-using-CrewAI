# VentureScope — MultiAgent Startup Idea Evaluator

> **Five specialized CrewAI agents evaluate your startup idea with the rigor and frameworks used by top-tier VC funds like Sequoia, a16z, and Benchmark.**

---

## What It Does

VentureScope takes a raw startup idea and runs it through a five-agent AI pipeline that mirrors how a real VC fund screens deals. Each agent is a specialist with a distinct role and backstory. Together, they produce a structured investment memo, a quantitative 0-100 score, and a downloadable PDF report.

---

## The Agent Pipeline

```
Input: Startup Idea + Target + Region + Pricing + Team + Traction
         │
         ▼
┌─────────────────────┐
│  Agent 1            │  Problem Validator
│  Chief Problem      │  → Pain intensity, frequency, workarounds,
│  Officer            │    "why now" rationale, P/S fit verdict
└────────┬────────────┘
         │ context passed down
         ▼
┌─────────────────────┐
│  Agent 2            │  Market Researcher
│  Market Intelligence│  → Bottom-up TAM/SAM/SOM, competitor table,
│  Director           │    timing analysis, early adopter thesis
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Agent 3            │  Business Model Strategist
│  Revenue Architect  │  → Pricing tiers, unit economics (LTV:CAC,
│                     │    payback), 90-day GTM plan, growth flywheel
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Agent 4            │  Risk & Moat Analyst
│  Investment Risk    │  → 5-category risk matrix, 6-axis moat scoring,
│  Partner            │    red flags, critical assumptions
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Agent 5            │  VC Investment Memo Writer
│  Managing Director  │  → IC-style memo: thesis, comps table,
│                     │    "what needs to be true", preliminary verdict
└────────┬────────────┘
         │
         ▼
  Investment Score (0-100) + Radar Chart + PDF Export
```

---

## Key Features

| Feature | Detail |
|---------|--------|
| **5 Specialized Agents** | Each has a distinct role, goal, and professional backstory |
| **VC-Grade Prompts** | TAM/SAM/SOM, unit economics, moat scoring, IC memo format |
| **Investment Score** | Weighted 0-100 across Problem, Market, Biz Model, Execution, Moat |
| **Radar Chart** | Interactive Plotly visualization of the 5 scoring dimensions |
| **Real-Time Progress** | Live step-by-step agent status during analysis |
| **Investment Memo** | Full IC memo styled after Sequoia/a16z deal documents |
| **PDF Export** | Download the complete report as a formatted PDF |
| **OpenRouter Ready** | Works with any OpenAI-compatible model via OpenRouter |

---

## Tech Stack

- **AI Orchestration**: [CrewAI](https://github.com/crewAIInc/crewAI) v0.157+ — multi-agent pipeline
- **LLM**: OpenRouter (GPT-4o-mini default, swap for any model)
- **LLM Client**: LangChain OpenAI
- **UI**: Streamlit with custom CSS (Inter font, dark hero, radar chart)
- **Charts**: Plotly — interactive radar/spider chart
- **PDF**: fpdf2 — zero-dependency PDF generation
- **Env**: python-dotenv

---

## Quick Start

### 1. Clone & install

```bash
git clone https://github.com/YOUR_USERNAME/Startup-Idea-Evaluator-using-CrewAI.git
cd Startup-Idea-Evaluator-using-CrewAI

python -m venv venv
source venv/bin/activate        # Mac/Linux
# venv\Scripts\activate         # Windows

pip install -r requirements.txt
```

### 2. Configure environment

Copy `.env` and add your key:

```bash
cp .env .env.local
```

```env
# .env
OPENAI_API_KEY=sk-or-v1-...          # Your OpenRouter key
OPENAI_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=openai/gpt-4o-mini  # or anthropic/claude-sonnet-4-5 for better quality
```

Get a free OpenRouter API key at [openrouter.ai](https://openrouter.ai).

### 3. Run

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## Project Structure

```
├── app.py           # Streamlit UI — layout, CSS, agent orchestration
├── agents.py        # 5 CrewAI agent definitions (roles, goals, backstories)
├── tasks.py         # Task prompts with embedded VC frameworks and scoring markers
├── scoring.py       # Score parsing (regex) + Plotly radar chart
├── pdf_export.py    # fpdf2 PDF report generator
├── requirements.txt
├── .env             # API keys (never commit)
└── main.py          # Original prototype (kept for reference)
```

---

## Scoring System

Each agent's task ends with a structured score marker (e.g., `PROBLEM_SCORE: 8`). After all agents complete, these are parsed and combined into a weighted 0-100 Investment Score:

| Dimension | Weight | Source Agent |
|-----------|--------|--------------|
| Problem / Pain | 25% | Problem Validator |
| Market Size | 20% | Market Researcher |
| Business Model | 20% | Business Strategist |
| Execution Risk | 20% | Risk & Moat Analyst |
| Moat Strength | 15% | Risk & Moat Analyst |

**Score bands:**
- 🟢 75–100 — Strong Interest
- 🟡 55–74 — Watchlist
- 🟠 35–54 — Needs Work
- 🔴 0–34  — Pass

---

## Deploying to Streamlit Cloud

1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io) → New app
3. Set `app.py` as the entry point
4. Add your API keys under **Secrets** (same format as `.env`)
5. Deploy — shareable URL in seconds

---

## Improving Output Quality

Swap `OPENROUTER_MODEL` to a more capable model for significantly better analysis:

```env
OPENROUTER_MODEL=anthropic/claude-sonnet-4-5
# or
OPENROUTER_MODEL=openai/gpt-4o
```

Both are available on OpenRouter.

---

## Sample Output

Given the idea: *"AI voice bot for dermatology clinics to handle appointment booking and insurance pre-auth"*

The system produces:
- **Problem Score**: 8/10 — Hair-on-fire pain for front desk staff
- **Market Score**: 7/10 — ~$2.4B TAM in India's private clinic market
- **Investment Score**: 71/100 — **Watchlist**
- **Memo verdict**: Series A-ready if 3 pilot clinics reach 500+ bookings/month

---

## Author

**Suhaib Khan** — [Portfolio](#) · [LinkedIn](#) · [GitHub](#)

Built to demonstrate multi-agent AI system design, prompt engineering, and product thinking in the context of venture capital workflows.
