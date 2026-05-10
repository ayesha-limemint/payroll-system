# Phase 9b — UI Verification & Screenshot

Every session must produce a screenshot of the working UI. This phase runs after
all tests pass (Phase 9) and before the regression suite (Phase 10).

## Steps

1. **Start the Django dev server**
   Use `mcp__Claude_Preview__preview_start` with the `django` configuration in
   `.claude/launch.json`. This starts the server on port 8000 and reuses it if
   already running.

2. **Navigate to the feature in the browser**
   Use `mcp__Claude_Preview__preview_eval` with `window.location.href = '/path/';`
   to navigate to the URL defined in the functional plan's `## UI Component` section.

3. **Exercise the feature — golden path**
   Use `mcp__Claude_Preview__preview_fill` and `mcp__Claude_Preview__preview_click`
   to fill in the form with a representative test case and submit. Confirm the result
   with `mcp__Claude_Preview__preview_snapshot` — verify values match the expected output.

4. **Exercise one edge case**
   Use a boundary value (e.g. wage base limit, bracket boundary, zero deduction).
   Verify correct output via snapshot.

5. **Capture and save the screenshot**
   Use Playwright (already installed) to capture the page and save it to the repo:

   ```python
   from playwright.sync_api import sync_playwright

   with sync_playwright() as p:
       browser = p.chromium.launch()
       page = browser.new_page(viewport={"width": 820, "height": 700})
       page.goto("http://127.0.0.1:8000/<url-path>/")
       # fill form fields as needed for the golden path
       page.fill("#field-id", "value")
       page.click("button[type=submit]")
       page.wait_for_load_state("networkidle")
       page.screenshot(path="screenshots/day-N-YYYY-MM-DD-<feature-slug>.png", full_page=True)
       browser.close()
   ```

   Save to: `screenshots/day-N-YYYY-MM-DD-<feature-slug>.png`

   - N = session day number (matches the CHANGELOG Day N entry)
   - YYYY-MM-DD = today's date
   - feature-slug = kebab-case feature name (e.g. `federal-income-tax`, `nj-sdi-fli`)

   Example: `screenshots/day-5-2026-05-10-nj-sdi-fli.png`

   Read the saved file with the Read tool to confirm it rendered correctly.

6. **If screenshot capture fails**
   Note it in the session summary under `### Screenshot`:
   `Skipped — screenshot capture failed: [reason].`
   Do not block the session on this. Proceed to Phase 10.

Do not proceed to Phase 10 until the screenshot is saved (or the skip is noted).
