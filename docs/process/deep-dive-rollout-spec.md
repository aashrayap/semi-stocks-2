# Deep-Dive Rollout Spec

Date: 2026-04-08

## Visual Summary

```text
Pilot first
COHR
  -> prove the deep-dive workflow end-to-end
  -> verify report quality improves
  -> freeze the process
  -> run remaining names in parallel

Remaining after pilot
MU   INTC   TSM   LITE
```

## Goal

Close the structured coverage gap in `canonical/20-data/companies/` by proving the workflow on `COHR` first, then applying the same process in parallel to the remaining deep-dive names.

Target set from `config.yaml`:
- `CRWV` — already done
- `NVDA` — already done
- `COHR` — pilot
- `MU`
- `INTC`
- `TSM`
- `LITE`

## Why COHR First

- It is the cleanest consensus zone across Leopold, Baker, and SemiAnalysis.
- It is already called out as the strongest first deep dive in `docs/process/13f-pipeline-design.md`.
- It should improve both the thesis layer and the report without requiring new schema design first.
- It is lower-noise than `INTC` or `TSM`, and less cycle-timing-fragile than `MU`.

## Pilot Scope: COHR

Deliver one complete `COHR` packet through the existing lane:

```text
raw
  -> canonical/10-wiki/raw/<cohr-source-files>
  -> canonical/10-wiki/sources/<cohr-page>
  -> canonical/20-data/companies/COHR/<quarter>.yaml
  -> thesis/report consumption
```

Required outputs:
- `canonical/10-wiki/raw/` primary-source capture for the latest relevant COHR earnings / filings / source artifacts
- `canonical/10-wiki/sources/cohr-<quarter>.md` synthesized page
- `canonical/20-data/companies/COHR/<quarter>.yaml` structured deep dive
- any minimal thesis/report wiring needed for that data to show up downstream

## COHR Acceptance Criteria

The pilot is considered proven only if all of these are true:

1. **Traceable**
- Every material claim in the COHR company YAML can be traced back to a concrete raw or source artifact.

2. **Structured**
- The YAML includes, at minimum:
  - `financials`
  - `forward_claims`
  - `thesis_signals`
  - `positioning`

3. **Trade-relevant**
- The packet explains:
  - what COHR actually sells into the bottleneck
  - why COHR matters relative to peers
  - what would confirm the thesis next
  - what would break the thesis

4. **Report-visible**
- The canonical report changes in a visible way because of the new COHR structured data, not just because the file exists.

5. **Repeatable**
- The workflow can be written as a short checklist and reused for `MU`, `INTC`, `TSM`, and `LITE` without schema redesign.

## COHR Process

### Step 1: Raw capture
- Pull the latest primary source set for COHR:
  - earnings transcript
  - earnings release / investor presentation if needed
  - material company press releases relevant to pluggable optics / CPO
- Keep raw immutable.
- Prefer primary-source captures over compiled summaries.

### Step 2: Source synthesis
- Create a `canonical/10-wiki/sources/` page with:
  - key metrics
  - guidance
  - management claims
  - bottleneck mapping
  - links back to structured data

### Step 3: Structured company YAML
- Create `canonical/20-data/companies/COHR/<quarter>.yaml`.
- Use the lean company deep-dive template from `docs/process/13f-pipeline-design.md` as guidance, but align to the existing `CRWV` / `NVDA` schema so downstream code can consume it now.

### Step 4: Downstream proof
- Verify the company shows up correctly in synthesis/report output.
- Confirm the report gained something concrete:
  - claims due
  - thesis signals
  - improved optics-stage evidence

### Step 5: Freeze the checklist
- Convert the final working sequence into a short repeatable checklist for the remaining names.

## Parallel Rollout After COHR Passes

Only start this phase after the COHR proof gates pass.

Parallel batch:
- Worker 1: `MU`
- Worker 2: `INTC`
- Worker 3: `TSM`
- Worker 4: `LITE`

Rules:
- Each worker owns one ticker only.
- Write scope is limited to that ticker’s raw/source/company files.
- Shared files like `README.md`, `canonical/30-thesis/thesis.yaml`, or `canonical/40-engine/engine/` code should not be edited in parallel unless strictly necessary.
- Any shared downstream integration happens after the ticker packets are complete.

## Rollout Order After Pilot

If full 4-way parallelization is too noisy, use this fallback:

1. `MU`
2. `LITE`
3. `INTC`
4. `TSM`

Rationale:
- `MU` and `LITE` are most likely to change current report quality fast.
- `INTC` is high-value but more thesis-divergent.
- `TSM` is foundational, but less directly trade-expressive than the others.

## Risks

- Creating a COHR file that exists but does not improve the report.
- Mixing a new company schema with the current earnings YAML schema and breaking downstream assumptions.
- Using secondary-source summaries as “raw,” which weakens trust in the rest of the pipeline.
- Parallelizing too early before the COHR checklist is stable.

## Definition of Done

This rollout is done when:
- `COHR`, `MU`, `INTC`, `TSM`, and `LITE` all have structured company coverage in `canonical/20-data/companies/`
- each packet is traceable to raw/source evidence
- the report reflects those packets without manual reconstruction
- the backlog item on deep-dive coverage can be marked complete
