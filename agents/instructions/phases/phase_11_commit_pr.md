# Phase 11 — Commit, PR & Changelog

1. Final commit:
   `Day N: <feature name> — complete`

2. Push the feature branch to GitHub.

3. Open a Pull Request:
   - Title: `Day N: <feature name>`
   - Body: link to Drive daily brief + one-paragraph summary of what was built

4. Update `CHANGELOG.md` in the repo:
   - Add an entry under today's date: what was added, changed, or fixed
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
