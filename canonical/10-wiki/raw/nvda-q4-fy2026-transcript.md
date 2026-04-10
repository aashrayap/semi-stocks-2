# NVIDIA Q4 FY2026 Earnings Call

Source: Earnings call transcript (February 26, 2026)
Compiled from: NVIDIA Newsroom, Motley Fool, Yahoo Finance, Fortune, Ticker Report
Fiscal quarter: Q4 FY2026 (Nov 2025 – Jan 25, 2026)

---

## Participants

- **Toshiya Hari** — VP, Investor Relations
- **Jensen Huang** — CEO
- **Colette Kress** — CFO

## Financial Results

**Revenue:** $68.127 billion (+20% QoQ, +73% YoY)
**FY2026 Revenue:** $215.938 billion (+65% YoY)

### Revenue by Segment

| Segment | Q4 FY2026 | FY2026 | QoQ | YoY |
|---|---|---|---|---|
| Data Center | $62.3B | $193.7B | +22% | +75% |
| Gaming | $3.7B | $16.0B | -13% | +47% |
| Professional Visualization | $1.3B | $3.2B | +74% | +159% |
| Automotive & Robotics | $604M | $2.3B | +2% | +6% |
| Networking (within DC) | $11B | $31B | — | +3.5x |

### Profitability

| Metric | Q4 FY2026 | FY2026 |
|---|---|---|
| Gross Margin (GAAP) | 75.0% | 71.1% |
| Gross Margin (non-GAAP) | 75.2% | 71.3% |
| Operating Income (GAAP) | $44.3B | $130.4B |
| Operating Income (non-GAAP) | $46.1B | $137.3B |
| Net Income (GAAP) | $43.0B | $120.1B |
| Net Income (non-GAAP) | $39.6B | $117.0B |
| EPS diluted (GAAP) | $1.76 | $4.90 |
| EPS diluted (non-GAAP) | $1.62 | $4.77 |

### Cash Flow & Balance Sheet

| Metric | Q4 FY2026 | FY2026 |
|---|---|---|
| Operating Cash Flow | $36.2B | $102.7B |
| Free Cash Flow | $35.0B | $97.0B |
| CapEx | $1.3B | $6.0B |
| Cash & Marketable Securities | $62.6B | — |
| Accounts Receivable | $38.5B | — |
| Inventories | $21.4B | — |
| Short-term Debt | $1.0B | — |
| Long-term Debt | $7.5B | — |
| Shareholders' Equity | $157.3B | — |
| Total Assets | $206.8B | — |

### Capital Returns

- FY2026: $41.1B returned ($40.1B buybacks + $974M dividends)
- 43% of annual FCF returned
- $58.5B remaining authorization
- Supply commitments: $95.2B (up from $50.3B in Q3)

---

## Prepared Remarks

### Colette Kress (CFO)

Reported "record revenue, operating income, and free cash flow." Total revenue $68B, up 73% YoY. Data Center revenue reached $62B (+75% YoY, +22% sequential). Full-year Data Center hit $194B, representing nearly 13x growth since ChatGPT's emergence.

Networking revenue surged to $11B quarterly, exceeding 3.5x YoY. Annual networking exceeded $31B, more than 10x vs fiscal 2021 (Mellanox acquisition year).

Sovereign AI revenue surpassed $30B annually, tripling YoY, driven by Canada, France, Netherlands, Singapore, and UK.

Gaming revenue reached $3.7B (+47% YoY). Professional Visualization crossed $1B for the first time at $1.3B (+159% YoY, +74% sequential). Automotive generated $604M (+6% YoY).

"The single most important lever of our gross margins is actually delivering generational leads" through superior performance per watt and per dollar versus system costs.

Grace Blackwell systems represented roughly two-thirds of data center revenue.

Free cash flow totaled $35B quarterly and $97B annually. Capital returns reached $41B (43% of annual FCF) via repurchases and dividends.

Q1 guidance: revenue $78B (±2%), GAAP/non-GAAP gross margins at 74.9%/75% (±50bps).

Top five cloud providers' collective CapEx expectations increased nearly $120B since year-start, approaching $700B. These customers represent "a little over 50%" of data center revenue.

Noted that limited H200 products were approved for Chinese customers, but no revenue has materialized. Warned China-based competitors "have the potential to disrupt the structure of the global AI industry over the long term."

Reiterated that generational performance improvements—exceeding Moore's Law predictions—alongside per-dollar advantages sustain margins. Annual full-stack AI infrastructure delivery (six new chips this cycle) enables continued value delivery.

Starting Q1, stock-based compensation will be included in non-GAAP results.

### Jensen Huang (CEO)

Announced deepened partnerships:
- **OpenAI:** GPT-5.3 Codex training/inference on Grace Blackwell and NVLink 72 systems
- **Meta Superintelligence Labs:** deployment of millions of Blackwell and Rubin GPUs
- **Anthropic:** $10 billion NVIDIA investment
- **Groq:** Non-exclusive licensing agreement for low-latency inference technology

On Rubin platform: includes six chips, trains MoE models with "one-quarter" the GPUs and reduces inference token cost "up to 10x" versus Blackwell. First Vera Rubin samples shipped early that week, with production shipments targeted for H2 2026.

On GB300 NVL72: achieved "50x performance per watt" and "35x lower cost per token" versus Hopper. CUDA optimization delivered "five times better performance" on GB200 NVL72 within four months.

Spectrum-X Ethernet was called "a home run."

NVIDIA "doesn't ship nodes of computers, we ship racks of computers."

"In this new world of AI, compute is revenues. Without compute, there's no way to generate tokens. Without tokens, there's no way to grow revenues."

"Computing demand is growing exponentially. Enterprise adoption of agents is skyrocketing. Our customers are racing to invest in AI compute — the factories powering the AI industrial revolution."

On Meta ROI: GEM model drove "3.5x increase in ad clicks" on Facebook and "more than 1%" conversation gains on Instagram.

On Vera CPU: features fundamentally different architecture — single-port LPDDR5 design optimized for data-driven computing (data processing, pre-training, post-training). "Amdahl's Law" principles necessitate exceptionally fast single-threaded performance, which Vera delivers "off the charts" better than Grace.

---

## Q&A Session

**Vivek Arya (Bank of America):** Asked about customer CapEx sustainability given $700B projected cloud spending and compressed cash flows.

**Huang:** Emphasized "compute equals revenues" in AI era. Token generation directly drives customer revenues. Despite concerns about growth sustainability, agentic AI inflection creates exponential compute demand. Customers generating "$300-400 billion" in traditional computing now requiring orders of magnitude more capacity.

**Stacy Rasgon:** (Question addressed Vera Rubin ramp.)

**Kress:** Noted strong Vera demand with planned customer orders already placed for second-half ramp beginning.

**Atif Malik (Citi):** Questioned CUDA's importance amid inference workload dominance.

**Huang:** Detailed TensorRT-LLM inference stack optimization requiring novel parallelization algorithms atop CUDA. Agentic systems spawn multiple agents generating exponential tokens, necessitating high-speed inference. "Each token directly translates into revenues" for customers.

**Ben Reitzes (Melius Research):** Asked whether mid-70s long-term gross margins remain sustainable with 2027 supply visibility.

**Kress:** Reiterated that generational performance improvements—exceeding Moore's Law predictions—alongside per-dollar advantages sustain margins. Annual full-stack AI infrastructure delivery enables continued value delivery.

**Antoine Chiketan (New Street Research):** Explored space data center feasibility.

**Huang:** Assessed economics as "poor today" but improving. Space offers abundant energy via solar panels; however, conduction-only heat dissipation requires large radiators, making liquid cooling impractical. MPS and Hopper GPUs already deployed in space. Imaging applications — high-resolution processing via AI rather than transmitting petabytes earthside — represent compelling use cases.

**Mark Zapakos (Evercore ISI):** Clarified whether non-hyperscale customers drove faster Data Center growth.

**Huang and Kress:** Confirmed top-five cloud providers represent ~50% revenue but diversity expanding across AI model makers, enterprises, and edge deployments. CUDA's flexibility across language, vision, robotics, biology, and physics problems strengthens ecosystem diversity.

**Aaron Rakers (Wells Fargo):** Asked about Vera CPU standalone availability and architectural importance.

**Huang:** Noted Vera features fundamentally different architecture—single-port LPDDR5 design optimized for data-driven computing. "Amdahl's Law" principles necessitate exceptionally fast single-threaded performance, which Vera delivers "off the charts" better than Grace.

**Tim Arcuri:** Suggested $100B annual cash generation warrants aggressive share repurchases despite stock underperformance.

**Kress:** Emphasized ecosystem support priority — supplier capacity, early developers — alongside strategic investments. Repurchases and dividends continue under disciplined capital allocation.

**Jim Schneider (Goldman Sachs):** Asked whether $3-4 trillion 2030 data center CapEx projection holds, identifying key application drivers.

**Huang:** Reasoned through token-driven software economics. Classical computing demanded ~$300-400B annual investment; AI requires thousand-fold greater capacity. Every company generates tokens via "AI factories." Agentic AI inflection (recent months) and physical AI opportunity ahead drive confidence in secular growth beyond $700B current hyperscaler CapEx.

---

## Q1 FY2027 Guidance

- Revenue: $78.0B ±2%
- GAAP Gross Margin: 74.9% ±50bps
- Non-GAAP Gross Margin: 75.0% ±50bps
- GAAP OpEx: ~$7.7B
- Non-GAAP OpEx: ~$7.5B
- Tax Rate (FY2027): 17.0-19.0%
- China Data Center compute revenue excluded from outlook
