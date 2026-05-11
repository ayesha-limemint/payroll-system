"""
GitHub client for the payroll agent.
Handles branch creation, commits, pushes, and pull requests.

Setup: Requires GITHUB_TOKEN env var with repo scope.
"""
import os
import subprocess
from datetime import date

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
REPO_URL = "https://github.com/ayesha-limemint/payroll-system.git"


def get_branch_name(feature_name: str) -> str:
    """Returns the standard branch name for today's feature."""
    slug = feature_name.lower().replace(" ", "-").replace("_", "-")
    return f"feature/{date.today().isoformat()}-{slug}"


def create_branch(branch_name: str) -> None:
    """Create and push a new feature branch from main."""
    subprocess.run(["git", "checkout", "main"], check=True)
    subprocess.run(["git", "pull", "origin", "main"], check=True)
    subprocess.run(["git", "checkout", "-b", branch_name], check=True)
    subprocess.run(["git", "push", "-u", "origin", branch_name], check=True)


def commit_and_push(message: str, files: list = None) -> None:
    """Stage, commit, and push changes to the current branch."""
    if files:
        subprocess.run(["git", "add"] + files, check=True)
    else:
        subprocess.run(["git", "add", "-A"], check=True)
    subprocess.run(["git", "commit", "-m", message], check=True)
    subprocess.run(["git", "push"], check=True)


def open_pull_request(branch_name: str, title: str, body: str) -> str:
    """
    Open a Pull Request on GitHub.
    Returns the PR URL.
    Requires GitHub CLI (gh) to be installed and authenticated.
    """
    # TODO (Session 0): install and configure GitHub CLI
    # gh pr create --title "..." --body "..." --base main
    raise NotImplementedError("Configure GitHub CLI in Session 0")


def run_tests() -> tuple:
    """
    Run the full Django test suite.
    Returns (passed: bool, output: str)
    """
    result = subprocess.run(
        ["python", "manage.py", "test", "--verbosity=2"],
        capture_output=True, text=True
    )
    passed = result.returncode == 0
    return passed, result.stdout + result.stderr
