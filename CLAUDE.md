# Payroll System — Agent Bootstrap

## How to start a session

At the start of every session, do the following in order:

1. Read `agents/instructions/daily_agent.md` from this repo — this contains the full workflow instructions
2. Read the current state from Google Drive:
   - Check `daily_briefs/YYYY-MM-DD/` for today's date
   - Check `requests/pending/` for any feature requests from Ash
3. Determine the current phase using `agents/lib/state_machine.py`
4. Follow the instructions in `daily_agent.md` exactly from the current phase

## Important rules

- Never start implementation without both functional AND technical approval from Ash
- Never modify `agents/lib/` helper scripts without Ash explicitly asking
- The workflow is defined in `agents/instructions/daily_agent.md` — if Ash changes that file, follow the new version on the next session start
- Always prefix test commits with [RED] and implementation commits with [GREEN]
- Never push to main directly — always use feature branches and PRs

## To start

Say: "Continue today's payroll session" or "Start today's payroll session"
