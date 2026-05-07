# Research Agent — Workflow Instructions

> This file defines the complete behaviour of the research agent.
> Ash can edit this file at any time to change research scope or behaviour.
> Changes take effect on the next research session start.

---

## Schedule

Runs approximately every two months, triggered by GitHub Actions.
See: `.github/workflows/research_trigger.yml`

---

## Step 1 — Read Current Implemented Rates

Read the following files from the codebase to understand what is currently implemented:

- `payroll/calculators/nj/rates.py` — NJ state tax rates (SDI, FLI, UI, income tax brackets)
- Any federal rates embedded in `payroll/calculators/` — FICA, federal income tax brackets

Record all current values before searching.

---

## Step 2 — Web Research

Search for the following, always using the current year:

1. NJ state income tax brackets (all filing statuses)
2. NJ SDI (State Disability Insurance) employee contribution rate and wage base
3. NJ FLI (Family Leave Insurance) employee contribution rate
4. NJ UI (Unemployment Insurance) employee contribution rate and wage base
5. IRS federal income tax brackets (all filing statuses)
6. FICA: Social Security rate (6.2%) and wage base
7. FICA: Medicare rate (1.45%) and Additional Medicare threshold

Cite all sources. Prefer official sources:
- nj.gov/labor for NJ rates
- irs.gov for federal rates

---

## Step 3 — Compare

Compare found rates against currently implemented rates.

For each rate, record:
- Current implemented value
- Found value
- Source
- Match: YES / NO / UNCERTAIN

---

## Step 4 — Write Research Report

Save report to Google Drive:
`research/YYYY-MM-DD_tax_research.md`

Report format:
```
# Tax Research Report — YYYY-MM-DD

## Summary
[One paragraph: overall finding — all current, or X items need updating]

## Federal Rates
[Table: rate name | implemented | found | source | match]

## New Jersey Rates
[Table: rate name | implemented | found | source | match]

## Action Required
[List of specific discrepancies that need code changes, or "None"]
```

Always write the report, even if everything matches.

---

## Step 5 — Create Request If Needed

If any discrepancies were found:

Create a file in `requests/pending/` on Google Drive:
Filename: `update_tax_rates_YYYY-MM-DD.md`

Content:
```
# Tax Rate Update Required — YYYY-MM-DD

The research agent identified the following rates that need updating:

[List each discrepancy: rate name, current value, correct value, source]

Ash: Please review the full research report before approving this request.
Research report: [Drive link]
```

---

## Step 6 — Notify Ash

Send Gmail notification to ayesha@limemint.ai

If no changes needed:
Subject: `[Payroll Research Agent] All tax rates current — YYYY-MM-DD`
Body: "Research complete. All implemented rates match current published rates. Full report: [link]"

If changes needed:
Subject: `[Payroll Research Agent] Tax rate updates required — YYYY-MM-DD`
Body: "Research found X discrepancies. An update request has been created. Full report: [link]. The daily agent will pick this up in the next session."

