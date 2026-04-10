# Ash Map

This repo is organized as a propagation system, not a generic project tree.

## Wide To Narrow

```text
external evidence
  -> canonical/10-wiki/raw/
  -> canonical/10-wiki/sources/ and canonical/10-wiki/concepts/
  -> canonical/20-data/sources/ and canonical/20-data/companies/
  -> canonical/30-thesis/thesis.yaml
  -> canonical/40-engine/
  -> canonical/50-reports/
```

## Where Things Land

```text
canonical/10-wiki/raw/
  immutable source captures

canonical/10-wiki/sources/
  one-source summaries, earnings calls, 13F syntheses

canonical/10-wiki/concepts/
  durable learnings that survive any one quarter

canonical/20-data/companies/
  quarter/company packets: financials, forward claims, thesis signals

canonical/20-data/sources/
  structured fund or signal state

canonical/30-thesis/thesis.yaml
  the narrow control plane

canonical/40-engine/
  code that reads canonical state and renders outputs

canonical/50-reports/
  published artifacts

agents/
  drafts, alerts, logs, experiments, scheduled sidecar state
```

## How To Iterate

```text
read raw evidence
  -> form source summaries
  -> promote reusable ideas into concepts
  -> update structured company/source data
  -> tighten thesis only when evidence really changed
  -> render reports
  -> compare agent outputs against canonical outputs
```

Think in questions, not folders:
- What is raw evidence?
- What is durable learning?
- What is machine-readable state?
- What is the current thesis?
- What is a published output?
- What should stay sidecar-only?

## Agent Boundary

```text
canonical/*  ->  agents/*  ->  human review  ->  optional promotion back to canonical/*
```

Agents may read canonical state broadly. They should write sidecar data under `agents/` unless a reviewed promotion is intentional.

## Practical Loop

1. Ingest or observe a source.
2. Write the smallest correct summary.
3. Promote repeated patterns into concepts.
4. Update the structured company packet or thesis only when the evidence actually changed.
5. Regenerate the engine and reports.
6. Use the delta to decide the next research step.

The useful mental model is not "where do I store this file?" but "how far through the funnel has this fact actually propagated?"
