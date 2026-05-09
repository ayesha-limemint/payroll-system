# Phase 7 — Create Feature Branch

**First, ensure the branch starts from the latest main:**

```bash
git checkout main
git pull origin main
```

Then create the feature branch using this naming convention:
`feature/YYYY-MM-DD-<feature-name-in-kebab-case>`

Example: `feature/2026-05-10-nj-state-income-tax`

```bash
git checkout -b feature/YYYY-MM-DD-<feature-name>
```

Push the branch to GitHub.

Then proceed immediately to Phase 8.
