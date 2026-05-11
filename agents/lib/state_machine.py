"""
State machine for the payroll agent.
Determines the current phase by reading Google Drive and GitHub state.

IMPORTANT: The agent never skips unfinished work.
It always finds the oldest unfinished session and resumes it,
regardless of how many days have passed.
"""
from agents.lib.drive_client import read_file, list_files
from datetime import date


class Phase:
    QUESTIONS = 2        # Milton has questions — waiting for Ash's answers
    FUNCTIONAL_PLAN = 3
    FUNCTIONAL_APPROVAL = 4
    TECHNICAL_PLAN = 5
    TECHNICAL_APPROVAL = 6
    CREATE_BRANCH = 7
    WRITE_TESTS = 8
    IMPLEMENT = 9
    REGRESSION = 10
    COMMIT_AND_PR = 11
    SESSION_SUMMARY = 12
    NOTIFY_COMPLETE = 13


class SessionState:
    """Represents the full state of a session — which date and which phase."""
    def __init__(self, date_str: str, phase: int, brief_path: str):
        self.date_str = date_str      # e.g. "2026-05-08"
        self.phase = phase            # Phase constant
        self.brief_path = brief_path  # Drive path to the daily_briefs/YYYY-MM-DD folder
        self.is_carry_over = date_str != date.today().isoformat()


def get_plan_status(plan_path: str) -> str:
    """
    Read the Status field from a plan document on Drive.
    Returns: PENDING_REVIEW, APPROVED, CHANGES_REQUESTED, or NOT_FOUND
    """
    try:
        content = read_file(plan_path)
        for line in content.splitlines():
            if line.startswith("Status:"):
                return line.split(":", 1)[1].strip()
    except Exception:
        pass
    return "NOT_FOUND"


def get_written_timestamp(plan_path: str) -> str | None:
    """
    Read the Written: timestamp field from a plan document.
    Returns the timestamp string or None if not found.
    """
    try:
        content = read_file(plan_path)
        for line in content.splitlines():
            if line.startswith("Written:"):
                return line.split(":", 1)[1].strip()
    except Exception:
        pass
    return None


def get_ash_notes(plan_content: str) -> list:
    """
    Extract all lines prefixed with 'Ash:' from a plan document.
    Returns a list of note strings.
    """
    notes = []
    for line in plan_content.splitlines():
        stripped = line.strip()
        if stripped.startswith("Ash:"):
            notes.append(stripped[4:].strip())
    return notes


def find_active_session() -> SessionState:
    """
    Find the active session on Drive and return its state.

    Logic:
    1. List all dated folders under daily_briefs/
    2. Find the most recent one
    3. If it is COMPLETE (or none exist), start a fresh session for today
    4. If it is not COMPLETE, resume it

    There is only ever one unfinished session at a time — the agent never
    starts a new session until the previous one reaches Status: COMPLETE.
    So checking the most recent folder is always sufficient.
    """
    today = date.today().isoformat()

    try:
        folders = list_files("daily_briefs")
    except Exception:
        folders = []

    # Filter to valid YYYY-MM-DD folders and find the most recent
    dated_folders = sorted(
        [f for f in folders if _is_date_folder(f)]
    )

    if dated_folders:
        most_recent = dated_folders[-1]
        brief_path = f"daily_briefs/{most_recent}"
        functional_plan = f"{brief_path}/01_functional_plan.md"
        functional_status = get_plan_status(functional_plan)

        if functional_status != "COMPLETE":
            # Resume the unfinished session
            phase = _determine_phase_for_session(brief_path)
            return SessionState(
                date_str=most_recent,
                phase=phase,
                brief_path=brief_path
            )

    # Most recent session is complete (or no sessions exist) — start fresh today
    today_path = f"daily_briefs/{today}"
    return SessionState(
        date_str=today,
        phase=Phase.FUNCTIONAL_PLAN,
        brief_path=today_path
    )


def _determine_phase_for_session(brief_path: str) -> int:
    """
    Given a brief folder path, determine which phase this session is at.
    Checks for questions doc first — that takes priority over everything else.

    Approval gates (phases 4 and 6) are retired: Milton proceeds from
    functional plan → technical plan → implementation without waiting.
    The only blocking condition is unanswered questions (Phase 2a).
    """
    questions_doc = f"{brief_path}/00_questions.md"
    functional_plan = f"{brief_path}/01_functional_plan.md"
    technical_plan = f"{brief_path}/02_technical_plan.md"

    questions_status = get_plan_status(questions_doc)
    functional_status = get_plan_status(functional_plan)
    technical_status = get_plan_status(technical_plan)

    # Questions doc exists and is still awaiting answers — only blocking condition
    if questions_status == "AWAITING_ANSWERS":
        return Phase.QUESTIONS

    # Functional plan not written yet
    if functional_status == "NOT_FOUND":
        return Phase.FUNCTIONAL_PLAN

    # Technical plan not written yet (functional plan exists — no approval needed)
    if technical_status == "NOT_FOUND":
        return Phase.TECHNICAL_PLAN

    # Both plans exist — proceed to implementation
    # TODO: wire up branch detection via github_client
    return Phase.CREATE_BRANCH


def _is_date_folder(name: str) -> bool:
    """Check if a folder name looks like a valid YYYY-MM-DD date."""
    try:
        from datetime import datetime
        datetime.strptime(name, "%Y-%m-%d")
        return True
    except ValueError:
        return False
