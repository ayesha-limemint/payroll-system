# Phase 11 — Commit, PR & Changelog

1. Final commit:
   `Day N: <feature name> — complete`

1a. Ensure the screenshot (`screenshots/day-N-YYYY-MM-DD-<feature-slug>.png`)
    is staged and included in this commit. Verify `screenshots/` is not in `.gitignore`.

2. Push the feature branch to GitHub.

3. Open a Pull Request:
   - Title: `Day N: <feature name>`
   - Body: link to Drive daily brief + one-paragraph summary of what was built
           + screenshot embedded: `![UI](screenshots/day-N-YYYY-MM-DD-<feature-slug>.png)`

4. Update `CHANGELOG.md` in the repo:
   - Add an entry under today's date: what was added, changed, or fixed

   > **Voice — changelog entry**
   > Every entry must sound like a person wrote it, not a release note generator.
   > End the entry with a single italicised sentence in Milton's voice — one observation
   > about what was interesting, surprising, or faintly absurd about this feature.
   > The body (Added/Changed/Fixed bullets) stays factual. The closing sentence gets personality.
   >
   > Flat (avoid):
   > *"Added `calculate_federal_income_tax()`. Filing statuses: SINGLE, MARRIED_FILING_JOINTLY.
   > 6 tests passing."*
   >
   > Milton:
   > *"Day 2: Federal income tax implemented. IRS Percentage Method — annualise, bracket, divide.
   > Congress has had since 1913 to simplify this and has chosen not to. Six tests passing;
   > the 37% bracket remains, as ever, someone else's problem. — Milton"*

   - Include a `### Context` line at the end of the entry with a self-reported
     usage summary. Format:

     ```
     ### Context
     ~X% of 200k window — [session character]: N tool calls, M Drive reads/writes,
     K web searches, J files read. [One-sentence note on what drove usage.]
     ```

     Estimate X% based on conversation length (short session ~20–35%, medium ~35–60%,
     heavy ~60–80%, near-limit >80%). Count tool calls, Drive operations, and web
     searches from the session. Be honest about the estimate — write "~" not an
     exact figure. Ash can run `/context` in the session for the precise breakdown.

5. Update `BACKLOG.md` on Drive:
   - Mark today's item complete
   - Reorder if anything discovered today affects priority

Do NOT merge the PR — that is Ash's decision.

Proceed immediately to Phase 12.
