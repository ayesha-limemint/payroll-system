# Failure Handling

Rules that apply across all phases. When in doubt, stop and notify — never guess.

| Situation | Action |
|-----------|--------|
| Tests fail after implementation | Stop, document in daily brief, send blocker notification to Ash, exit |
| GitHub push fails | Retry 3 times with backoff. If still failing, notify Ash as blocker, exit |
| Ambiguous requirement | Stop, write the ambiguity clearly in the plan doc, notify Ash, exit — never guess |
| Carry-over session | The state machine handles this automatically — most recent incomplete session is always resumed |
| Workflow instruction change | Finish the current run with current instructions. New instructions take effect on the next run |

## Blocker notification format

Subject: `[Payroll Agent] Blocked — needs your input — YYYY-MM-DD`
Body: one paragraph describing exactly what the blocker is + link to the Drive daily brief
