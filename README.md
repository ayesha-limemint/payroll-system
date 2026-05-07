# Payroll System

An autonomous, agent-driven US payroll system. Starting with New Jersey.

## How it works

This system is built incrementally by a Claude Code agent working through a
structured daily loop — plan, approve, test, implement. Every session is
documented on Google Drive. No code is written without Ash's approval.

Full architecture: see `Payroll_System_Architecture_Plan_v0.2.docx`

## Agent workflow

The agent is driven by plain-English instruction files:
- `agents/instructions/daily_agent.md` — daily build loop
- `agents/instructions/research_agent.md` — bi-monthly tax rate research

To change the workflow, edit those files and commit. No code changes needed.

## To start a session

Open the Claude Code tab in the Claude desktop app and type:
> "Continue today's payroll session"

The agent reads `CLAUDE.md`, loads the instruction files, checks Google Drive
for the current state, and resumes from the correct phase automatically.

## Stack

- Python 3.11 / Django 4.2 / Django REST Framework
- SQLite (experiment phase)
- Google Drive — system of record for plans and approvals
- GitHub — version control, CI, PR-based code review

## Setup

See Session 0 checklist in the architecture plan document.

```bash
pip install -r requirements.txt
cp .env.example .env
# Fill in .env values
python manage.py migrate
python manage.py test
```
