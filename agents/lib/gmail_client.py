"""
Gmail client for the payroll agent.
Uses Application Default Credentials (ADC) — no service account JSON needed.

Run once to authenticate: gcloud auth application-default login
Scopes required: gmail.send
"""
import base64
import os
from email.message import EmailMessage

from google.auth import default
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/gmail.send",
]

ASH_EMAIL = "ayesha@limemint.ai"


def _service():
    """Build and return an authenticated Gmail service."""
    credentials, _ = default(scopes=SCOPES)
    return build("gmail", "v1", credentials=credentials)


def send_notification(subject: str, body: str) -> None:
    """
    Send a notification email to Ash.
    Subject should be prefixed with [Payroll Agent] by convention.
    Body should be concise — one paragraph max — always include a direct link.
    """
    service = _service()
    message = EmailMessage()
    message["To"] = ASH_EMAIL
    message["Subject"] = subject
    message.set_content(body)

    encoded = base64.urlsafe_b64encode(message.as_bytes()).decode()
    service.users().messages().send(
        userId="me", body={"raw": encoded}
    ).execute()


def send_functional_plan_ready(date_str: str, drive_url: str, summary: str) -> None:
    """Notify Ash that the functional plan is ready for review."""
    send_notification(
        subject=f"[Payroll Agent] Functional plan ready for review — {date_str}",
        body=f"{summary}\n\nReview here: {drive_url}"
    )


def send_technical_plan_ready(date_str: str, drive_url: str, summary: str) -> None:
    """Notify Ash that the technical plan is ready for review."""
    send_notification(
        subject=f"[Payroll Agent] Technical plan ready for review — {date_str}",
        body=f"{summary}\n\nReview here: {drive_url}"
    )


def send_session_complete(date_str: str, drive_url: str, pr_url: str, summary: str) -> None:
    """Notify Ash that today's session is complete."""
    send_notification(
        subject=f"[Payroll Agent] Session complete — {date_str}",
        body=f"{summary}\n\nSession summary: {drive_url}\nGitHub PR: {pr_url}"
    )


def send_reminder(date_str: str, plan_type: str, drive_url: str) -> None:
    """Send a 24-hour reminder that a plan is still awaiting review."""
    send_notification(
        subject=f"[Payroll Agent] Reminder: {plan_type} plan awaiting your review — {date_str}",
        body=f"This plan has been waiting for your review for over 24 hours.\n\nReview here: {drive_url}"
    )


def send_blocker(date_str: str, description: str, drive_url: str) -> None:
    """Notify Ash that the agent is blocked and needs her input."""
    send_notification(
        subject=f"[Payroll Agent] Blocked — needs your input — {date_str}",
        body=f"{description}\n\nDetails: {drive_url}"
    )


def send_session_ready(date_str: str) -> None:
    """Morning trigger notification — sent by GitHub Actions."""
    send_notification(
        subject=f"[Payroll Agent] Today's session is ready — {date_str}",
        body=(
            f"The daily build session for {date_str} is ready to run.\n\n"
            "Open the Claude Code tab and type: \"Continue today's payroll session\""
        )
    )
