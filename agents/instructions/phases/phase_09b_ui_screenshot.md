# Phase 9b — UI Verification & Screenshot

Every session must produce a screenshot of the working UI. This phase runs after
all tests pass (Phase 9) and before the regression suite (Phase 10).

## Steps

1. **Start the Django dev server**
   ```
   python manage.py runserver
   ```

2. **Navigate to the feature in the browser**
   Use available browser or preview tools (mcp__Claude_Preview or mcp__Claude_in_Chrome)
   to open the page defined in the functional plan's `## UI Component` section.

3. **Exercise the feature — golden path**
   Fill in the form using a representative test case from the technical plan.
   Submit it. Verify the result matches the expected output.

4. **Exercise one edge case**
   Use a boundary value (e.g. wage base limit, bracket boundary, zero deduction).
   Verify correct output.

5. **Capture the screenshot**
   Take a screenshot of the page showing the input fields and the computed result.
   Save it to the repo at:

   `screenshots/day-N-YYYY-MM-DD-<feature-slug>.png`

   - N = session day number (matches the CHANGELOG Day N entry)
   - YYYY-MM-DD = today's date
   - feature-slug = kebab-case feature name (e.g. `federal-income-tax`, `nj-sdi-fli`)

   Example: `screenshots/day-5-2026-05-10-nj-sdi-fli.png`

6. **If browser tools are unavailable**
   Note it in the session summary under `### Screenshot`:
   `Skipped — browser tools unavailable this session.`
   Do not block the session on this. Proceed to Phase 10.

Do not proceed to Phase 10 until the screenshot is saved (or the skip is noted).
