# Technical Plan — [Feature Name] — YYYY-MM-DD

Status: PENDING_REVIEW
Approved by: —
Ash Notes: —
Written: YYYY-MM-DD HH:MM UTC

---

## Reference
- Functional plan: [link to 01_functional_plan.md on Drive]
- Feature branch: feature/YYYY-MM-DD-[feature-name]

---

## 1. Files to Create
> List every new file that will be created in this session.

| File path | Purpose |
|-----------|---------|
| | |

---

## 2. Files to Modify
> List every existing file that will be changed, and what will change.

| File path | What changes |
|-----------|-------------|
| | |

---

## 3. Django Models
> Describe any new or modified models. Write "None" if no model changes.

None

---

## 4. API Contract
> Define the endpoint exactly. Write "None" if no API changes.

**Endpoint:** `METHOD /api/v1/[path]`

**Request body:**
```json
{
  "field": "type — description"
}
```

**Response (200):**
```json
{
  "field": "type — description"
}
```

**Error responses:**
- `400` — [when and why]
- `422` — [when and why]

---

## 5. Key Functions / Classes
> List the main functions or classes to be written with their signatures.

```python
def function_name(param: type) -> return_type:
    """One-line description."""
    ...
```

---

## 6. Test Cases
> Map each functional scenario to a concrete Django test case.
> Every scenario from the functional plan must appear here.

| Scenario (from functional plan) | Test method name | Input | Expected output |
|--------------------------------|-----------------|-------|----------------|
| | | | |

---

## 7. Dependencies
> List any existing code this feature depends on.

- [file or function this builds on]

---

## 8. Out of Scope
> Explicitly list what will NOT be done in this session.

- [item out of scope]

---

## 9. Risks / Notes
> Anything the agent wants Ash to be aware of before approving.

None

---
_Template version: 1.0 — edit this file in the repo to change the format for all future technical plans_
