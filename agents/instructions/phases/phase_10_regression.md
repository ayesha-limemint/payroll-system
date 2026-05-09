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
   - Send Ash a Slack blocker notification: `[Milton] Blocked — regression failure — YYYY-MM-DD` + Drive link
   - Do NOT push broken code
   - Exit

If all tests pass, proceed immediately to Phase 11.
