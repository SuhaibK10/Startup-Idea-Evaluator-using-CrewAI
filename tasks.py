from crewai import Task
from crewai.agents.agent_builder.base_agent import BaseAgent


_VALIDATE_DESC = """\
Evaluate the startup idea below with the rigor of a top VC fund's initial screening.

STARTUP CONTEXT:
{ctx}

Deliver a structured analysis:

## 1. Problem Statement
One crisp, memorable sentence that captures the core pain.

## 2. Pain Assessment
- **Intensity (1-10):** How severe is this? Mild inconvenience → existential crisis.
- **Frequency:** Daily / Weekly / Monthly / Rare — with a concrete example.
- **Economic cost:** What does this problem cost the customer today (time, money, risk)?

## 3. Who Suffers Most
Define the most acutely affected customer archetype in specific terms
(e.g., "solo-practice dermatologists in Tier-2 Indian cities seeing 80+ patients/week,"
not just "doctors"). Specificity signals you understand the market.

## 4. Current Workarounds
List 3-5 things people do today instead of buying your solution.
No workarounds = problem may not be real. Expensive/painful workarounds = strong signal.

## 5. Why Now
What has changed in the last 2-3 years (tech, regulation, behaviour, infrastructure)
that makes this solvable or urgent today? A missing "why now" is a yellow flag.

## 6. Problem-Solution Fit
Does the proposed solution attack the root cause or a symptom?
Is it plausibly 10x better than the best current workaround?

## 7. Verdict
State one of: 🟢 Strong | 🟡 Moderate | 🔴 Weak
Provide 3 concise bullet points justifying the verdict.

End your response with EXACTLY this line (replace X with an integer 1-10):
PROBLEM_SCORE: X
"""

_RESEARCH_DESC = """\
Conduct a rigorous market analysis for the startup described below.

STARTUP CONTEXT:
{ctx}

PROBLEM VALIDATOR OUTPUT (use as context):
{prior}

## 1. Market Sizing — Bottom-Up
- **TAM** (Total Addressable Market): Global opportunity if fully captured.
- **SAM** (Serviceable Addressable Market): Realistic segment given geography/language/regulation.
- **SOM** (Serviceable Obtainable Market): Achievable in 3 years with solid execution.
Show the core assumption driving each number (e.g., "X clinics × $Y ARPU × Z% penetration").

## 2. Competitive Landscape
Build a comparison table for 4-6 competitors (direct + indirect):

| Player | Category | Est. Funding | Key Weakness |
|--------|----------|--------------|--------------|
| ...    | ...      | ...          | ...          |

## 3. Market Timing
Is this market early-stage, high-growth, or maturing? List 2-3 macro tailwinds AND 1-2 headwinds.

## 4. Unique Angle
What specific edge does this startup have that the others lack?
(Tech, distribution, pricing model, regulatory insight, community, data?)

## 5. Early Adopter Profile
Who will be the first 10 paying customers, and what will convince them to switch today?
What channel reaches them most efficiently?

## 6. Three Proprietary Bets
Name 3 non-obvious things you believe about this market that most people would disagree with.

End your response with EXACTLY this line (replace X with an integer 1-10):
MARKET_SCORE: X
"""

_BIZMODEL_DESC = """\
Design the revenue model and go-to-market strategy for this startup.

STARTUP CONTEXT:
{ctx}

PRIOR ANALYSIS (use as context):
{prior}

## 1. Revenue Model Recommendation
State the primary model (Subscription / Usage-based / Marketplace / etc.) and why.
Show a 3-tier pricing structure with package names and price points:
| Tier | Price | Target Customer | Key Features |
|------|-------|----------------|--------------|

## 2. Unit Economics (Year 2 Estimate)
Build a simple model:
- **ARPU**: Annual revenue per customer
- **Gross Margin**: % (SaaS target: ≥70%)
- **CAC**: Blended cost to acquire one customer (break down by top channel)
- **LTV**: = ARPU × Gross Margin% × Avg. Lifetime (years)
- **LTV:CAC Ratio**: (target: ≥3x; ideal: ≥5x)
- **Payback Period**: Months to recover CAC (target: <18 months)

Show the math explicitly, even with rough numbers.

## 3. 90-Day GTM Plan
- **Month 1 (First 10 Customers):** Exact actions, channels, outreach strategy.
- **Month 2 (Reach 50 Customers):** What's working, double down on what.
- **Month 3 (Reach 100 Customers):** Referral loop, partnership, or content play.

## 4. Revenue Milestones
- $100K ARR: How many customers at what ARPU? When realistically?
- $1M ARR: The Series A unlock. What does the business look like?

## 5. Growth Flywheel
Describe the compounding mechanism in 2-3 sentences.
(Network effects / data moat / switching costs / distribution lock-in?)

End your response with EXACTLY this line (replace X with an integer 1-10):
BIZMODEL_SCORE: X
"""

_RISK_DESC = """\
Conduct a thorough risk and moat assessment for this startup.

STARTUP CONTEXT:
{ctx}

PRIOR ANALYSIS (use as context):
{prior}

## 1. Risk Matrix
For each risk: **Probability** (H/M/L) × **Impact** (H/M/L) → overall rating.

### Product & Technical Risks
(3-4 specific risks with probability, impact, and one mitigation each)

### Market & Timing Risks
(3-4 specific risks)

### Execution & Team Risks
(2-3 specific risks)

### Legal, Regulatory & Compliance Risks
(2-3 risks — especially important for healthtech, fintech, edtech, etc.)

### Competitive Risks
(Include: "What if Google/Amazon/Salesforce builds this?" and the realistic threat level)

## 2. Moat Assessment
Rate each defensibility mechanism (0-10) and explain WHY:
| Moat Type | Score /10 | Rationale |
|-----------|-----------|-----------|
| Network Effects | | |
| Switching Costs | | |
| Data / AI Advantage | | |
| Brand & Trust | | |
| Regulatory Moat | | |
| Distribution Lock-in | | |

**Overall Moat Strength**: [Weak / Moderate / Strong] — one sentence summary.

## 3. Red Flags (Deal-Breakers)
List any factors that would cause a disciplined VC to pass immediately.

## 4. What Needs to Be True
5 critical assumptions that must be validated in the first 90 days.

End your response with EXACTLY these two lines (replace X and Y with integers 1-10):
RISK_SCORE: X
MOAT_SCORE: Y
"""

_MEMO_DESC = """\
Write a professional investment committee memo for this startup.
Base it on ALL prior agent analyses. Be specific, honest, and VC-grade.

STARTUP CONTEXT:
{ctx}

FULL ANALYSIS FROM ALL PRIOR AGENTS:
{prior}

Follow this EXACT structure:

---

# INVESTMENT MEMO

**Company**: [Derive a plausible startup name from the idea]
**Stage**: [Pre-Seed / Seed / Series A — based on traction signals]
**Recommended Ask**: [Estimated appropriate funding amount]
**Sector**: [Category — e.g., HealthTech SaaS, B2B Fintech, etc.]

---

## ONE-LINE PITCH
A single sentence that captures what the company does, for whom, and why it matters.

## THE OPPORTUNITY IN ONE PARAGRAPH
Market size, the core pain, the timing unlock, and why this team should win.
(4-5 sentences; this is what a partner reads before deciding whether to take a meeting.)

## INVESTMENT THESIS
Three reasons this could be a 10x return:
1. **[Thesis Title]**: [2-3 sentence argument]
2. **[Thesis Title]**: [2-3 sentence argument]
3. **[Thesis Title]**: [2-3 sentence argument]

## WHAT WE LIKE
- [Specific strength with concrete evidence from the analysis]
- [Specific strength]
- [Specific strength]
- [Specific strength]

## KEY CONCERNS
- [Concern 1 + why it matters to the investment thesis]
- [Concern 2 + why it matters]
- [Concern 3 + why it matters]

## WHAT NEEDS TO BE TRUE
For this to be a fund-returning investment from seed:
- [ ] [Critical assumption 1]
- [ ] [Critical assumption 2]
- [ ] [Critical assumption 3]
- [ ] [Critical assumption 4]

## COMPARABLE COMPANIES
| Company | Stage at Funding | Amount Raised | Outcome / Status |
|---------|-----------------|---------------|-----------------|
| [Name]  | [Stage]         | $[X]M         | [Status]        |
| [Name]  | [Stage]         | $[X]M         | [Status]        |
| [Name]  | [Stage]         | $[X]M         | [Status]        |

## PRELIMINARY VERDICT
**[🟢 Strong Interest | 🟡 Watchlist | 🟠 Needs Work | 🔴 Pass]**

[2-3 sentence justification that a partner would actually say in an IC meeting.]

**Recommended Next Steps:**
1. [Specific diligence action]
2. [Specific diligence action]
3. [Specific diligence action]

---
"""


def make_validate_task(agent: BaseAgent, problem_ctx: str) -> Task:
    return Task(
        description=_VALIDATE_DESC.format(ctx=problem_ctx),
        agent=agent,
        expected_output=(
            "Structured problem analysis covering pain intensity, workarounds, "
            "why-now rationale, and a Green/Yellow/Red verdict. "
            "Ends with PROBLEM_SCORE: [1-10]."
        ),
    )


def make_research_task(agent: BaseAgent, problem_ctx: str, prior: str) -> Task:
    return Task(
        description=_RESEARCH_DESC.format(ctx=problem_ctx, prior=prior or "Not yet available."),
        agent=agent,
        expected_output=(
            "TAM/SAM/SOM with methodology, competitor table, market timing, "
            "early adopter profile, and three proprietary bets. "
            "Ends with MARKET_SCORE: [1-10]."
        ),
    )


def make_bizmodel_task(agent: BaseAgent, problem_ctx: str, prior: str) -> Task:
    return Task(
        description=_BIZMODEL_DESC.format(ctx=problem_ctx, prior=prior or "Not yet available."),
        agent=agent,
        expected_output=(
            "Revenue model, pricing tiers, unit economics with math, "
            "90-day GTM plan, and growth flywheel. "
            "Ends with BIZMODEL_SCORE: [1-10]."
        ),
    )


def make_risk_task(agent: BaseAgent, problem_ctx: str, prior: str) -> Task:
    return Task(
        description=_RISK_DESC.format(ctx=problem_ctx, prior=prior or "Not yet available."),
        agent=agent,
        expected_output=(
            "Risk matrix by category, moat table with scores, red flags, "
            "and critical assumptions. "
            "Ends with RISK_SCORE: [1-10] and MOAT_SCORE: [1-10]."
        ),
    )


def make_memo_task(agent: BaseAgent, problem_ctx: str, prior: str) -> Task:
    return Task(
        description=_MEMO_DESC.format(ctx=problem_ctx, prior=prior or "Not yet available."),
        agent=agent,
        expected_output=(
            "Full IC-style investment memo with one-line pitch, investment thesis, "
            "comparable companies table, and a preliminary verdict."
        ),
    )
