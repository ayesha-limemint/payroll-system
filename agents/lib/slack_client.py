"""
Slack client for the payroll agent.
Sends notifications to the #payroll-agent channel via incoming webhook.

Webhook URL is read from SLACK_WEBHOOK_URL in .env.
No auth setup required beyond adding the webhook URL to .env.
"""
import json
import os
import urllib.request

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")


def send_notification(text: str) -> None:
    """
    POST a message to the #payroll-agent Slack channel.
    text should lead with [Milton] per notification rules in daily_agent.md.
    Raises RuntimeError if the webhook URL is not configured.
    Raises urllib.error.URLError on network failure.
    """
    if not SLACK_WEBHOOK_URL:
        raise RuntimeError(
            "SLACK_WEBHOOK_URL is not set. Add it to .env to enable Slack notifications."
        )
    payload = json.dumps({"text": text}).encode("utf-8")
    req = urllib.request.Request(
        SLACK_WEBHOOK_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        if resp.status != 200:
            raise RuntimeError(f"Slack webhook returned {resp.status}")


def send_functional_plan_ready(date_str: str, drive_url: str, summary: str) -> None:
    """Phase 3 notification — functional plan written, proceeding to Phase 5."""
    send_notification(f"[Milton] {summary}\n{drive_url}")


def send_technical_plan_ready(date_str: str, drive_url: str, summary: str) -> None:
    """Phase 5 notification — technical plan written, proceeding to Phase 7."""
    send_notification(f"[Milton] {summary}\n{drive_url}")


def send_questions(date_str: str, drive_url: str, summary: str) -> None:
    """Phase 2a notification — blocked on unanswered questions."""
    send_notification(f"[Milton] {summary}\n{drive_url}")


def send_blocker(date_str: str, drive_url: str, summary: str) -> None:
    """Phase 10 notification — regression failure, needs Ash's input."""
    send_notification(f"[Milton] {summary}\n{drive_url}")


def send_session_complete(date_str: str, drive_url: str, pr_url: str, summary: str) -> None:
    """Phase 13 notification — session complete."""
    send_notification(
        f"[Milton] {summary}\nDrive: {drive_url}\nPR: {pr_url}\n— Milton"
    )
