# Thesis Proposals

This lane owns authored proposal decision records for thesis or company
admission changes.

Proposal state is the reader gate:

```text
proposed -> accepted | rejected
```

Only `accepted` proposals admit anything into the Signal Desk admitted universe.
`proposed` and `rejected` proposals stay internal and do not emit into the main
reader feed.

## Minimum Shape

```yaml
kind: thesis_proposal
schema_version: 1
id: proposal:example-company-admission
status: proposed
title: Example company admission
decision_question: Should company:example enter the current Signal Desk universe?
companies:
  - company_id: company:example
    ticker: EXAMPLE
    name: Example Inc.
    role_id: company-role:unknown
evidence_refs:
  - source_document_id: source-doc:example
    summary: Evidence summary.
decision:
  decided_by: null
  decided_at: null
  notes: ""
```

Accepted proposals must include at least one stable company reference and at
least one `evidence_refs[].source_document_id`. In this phase, accepted proposal
state is the sole admission authority; `reader_eligible` and `applied` are not
authored fields.
