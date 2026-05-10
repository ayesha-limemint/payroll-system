# Phase 9b — UI Verification & Screenshots

Every session must produce screenshots of the working UI. This phase runs after
all tests pass (Phase 9) and before the regression suite (Phase 10).

## Steps

1. **Start the Django dev server**
   Use `mcp__Claude_Preview__preview_start` with the `django` configuration in
   `.claude/launch.json`. This starts the server on port 8000 and reuses it if
   already running.

2. **Navigate to the feature in the browser**
   Use `mcp__Claude_Preview__preview_eval` with `window.location.href = '/path/';`
   to navigate to the URL defined in the functional plan's `## UI Component` section.

3. **Plan the screenshots**
   Before capturing, decide which states to show. Choose up to 10 that together
   demonstrate the feature fully. Good choices cover:
   - The empty form (before any submission)
   - The golden path result (a typical, correct calculation)
   - Edge cases from the test suite (wage base exhausted, zero gross, bracket boundary, etc.)
   - Any state that would be non-obvious without seeing it (e.g. UI=$0.00 while SDI/FLI are still active)

   Aim for enough to tell the full story. More is better than fewer, up to 10.

4. **Verify each state before capturing**
   Use `mcp__Claude_Preview__preview_fill`, `mcp__Claude_Preview__preview_click`,
   and `mcp__Claude_Preview__preview_snapshot` to exercise each state and confirm
   the output is correct before saving the screenshot.

5. **Capture and save all screenshots**
   Use a single Playwright script to capture every planned state in one run:

   ```python
   from playwright.sync_api import sync_playwright

   with sync_playwright() as p:
       browser = p.chromium.launch()
       page = browser.new_page(viewport={"width": 820, "height": 700})

       # Screenshot 1: empty form
       page.goto("http://127.0.0.1:8000/<url-path>/")
       page.screenshot(path="screenshots/day-N-YYYY-MM-DD-<slug>-01-empty.png", full_page=True)

       # Screenshot 2: golden path result
       page.fill("#field-id", "value")
       page.click("button[type=submit]")
       page.wait_for_load_state("networkidle")
       page.screenshot(path="screenshots/day-N-YYYY-MM-DD-<slug>-02-golden-path.png", full_page=True)

       # Screenshot 3..N: edge cases
       # (navigate back, fill different values, submit, screenshot)

       browser.close()
   ```

   **Naming convention:**
   `screenshots/day-N-YYYY-MM-DD-<feature-slug>-NN-<label>.png`

   - `N` = session day number
   - `YYYY-MM-DD` = today's date
   - `feature-slug` = kebab-case feature name (e.g. `nj-sdi-fli`)
   - `NN` = two-digit sequence number (01, 02, 03...)
   - `label` = one or two words describing this state (e.g. `empty`, `golden-path`, `ui-exhausted`, `all-caps-done`)

   Example set for Day 5:
   ```
   screenshots/day-5-2026-05-10-nj-sdi-fli-01-empty.png
   screenshots/day-5-2026-05-10-nj-sdi-fli-02-golden-path.png
   screenshots/day-5-2026-05-10-nj-sdi-fli-03-crosses-ui-base.png
   screenshots/day-5-2026-05-10-nj-sdi-fli-04-ui-exhausted.png
   screenshots/day-5-2026-05-10-nj-sdi-fli-05-all-caps-done.png
   ```

   Read at least the first and last saved files with the Read tool to confirm they
   rendered correctly before proceeding.

6. **If screenshot capture fails**
   Note it in the session summary under `### Screenshots`:
   `Skipped — screenshot capture failed: [reason].`
   Do not block the session on this. Proceed to Phase 10.

Do not proceed to Phase 10 until the screenshots are saved (or the skip is noted).
