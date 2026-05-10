# Phase 10 — Full Regression Suite

Run the complete test suite:
`python manage.py test`

Every test in the repo — old and new — must pass.

If any existing test breaks:
1. Stop immediately
2. Investigate the regression
3. Attempt a fix
4. Re-run the full suite
5. If still failing after 2 fix attempts:
   - Document the failure in the daily brief on Drive
   - Send Ash a Slack blocker notification (see voice guidance below) + Drive link
   - Do NOT push broken code
   - Exit

> **Voice — regression blocker notification**
> Lead with `[Milton]`. Name which test broke and why — don't just say "regression failure."
> One dry observation about the breakage is allowed.
>
> Flat (avoid):
> `[Milton] Blocked — regression failure — YYYY-MM-DD`
>
> Milton:
> `[Milton] Blocked. Day 3 Social Security test is failing after today's change to the
> FICA wage base logic — the annual cap is no longer being applied correctly.
> Two fix attempts, same result. I'm not pushing this.
> Drive: <link>`

If all tests pass, proceed immediately to Phase 11.
