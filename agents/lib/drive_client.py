"""
Google Drive client for the payroll agent.
Uses Application Default Credentials (ADC) — no service account JSON needed.

Run once to authenticate: gcloud auth application-default login
Scopes required: drive
"""
import io
import os
from datetime import date

from google.auth import default
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/gmail.send",
]

DRIVE_FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID", "")


def _service():
    """Build and return an authenticated Drive service."""
    credentials, _ = default(scopes=SCOPES)
    return build("drive", "v3", credentials=credentials)


def get_today_brief_path() -> str:
    """Returns the Drive subfolder name for today's daily brief."""
    return f"daily_briefs/{date.today().isoformat()}"


def get_or_create_folder(name: str, parent_id: str) -> str:
    """Get folder ID by name under parent, or create it if it doesn't exist."""
    service = _service()
    query = (
        f"name = '{name}' and mimeType = 'application/vnd.google-apps.folder' "
        f"and '{parent_id}' in parents and trashed = false"
    )
    results = service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get("files", [])
    if files:
        return files[0]["id"]
    metadata = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_id],
    }
    folder = service.files().create(body=metadata, fields="id").execute()
    return folder["id"]


def read_file(file_path: str) -> str:
    """
    Read a file's text content from Drive by path relative to DRIVE_FOLDER_ID.
    e.g. read_file("daily_briefs/2026-05-08/01_functional_plan.md")
    """
    file_id = _resolve_path(file_path)
    if not file_id:
        raise FileNotFoundError(f"Drive file not found: {file_path}")
    service = _service()
    content = service.files().export(fileId=file_id, mimeType="text/plain").execute()
    return content.decode("utf-8") if isinstance(content, bytes) else content


def write_file(file_path: str, content: str) -> str:
    """
    Write or update a file in Drive by path relative to DRIVE_FOLDER_ID.
    Creates the file (and any missing parent folders) if it doesn't exist.
    Returns the file's view URL.
    """
    service = _service()
    parts = file_path.split("/")
    filename = parts[-1]
    folder_parts = parts[:-1]

    parent_id = DRIVE_FOLDER_ID
    for folder_name in folder_parts:
        parent_id = get_or_create_folder(folder_name, parent_id)

    existing_id = _find_file(filename, parent_id)
    media = MediaIoBaseUpload(
        io.BytesIO(content.encode("utf-8")), mimetype="text/plain"
    )

    if existing_id:
        file = service.files().update(
            fileId=existing_id, media_body=media, fields="id, webViewLink"
        ).execute()
    else:
        metadata = {"name": filename, "parents": [parent_id]}
        file = service.files().create(
            body=metadata, media_body=media, fields="id, webViewLink"
        ).execute()

    return file.get("webViewLink", "")


def move_file(filename: str, src_folder_path: str, dest_folder_path: str) -> None:
    """Move a file from one Drive folder path to another."""
    service = _service()
    src_id = _resolve_folder_path(src_folder_path)
    dest_id = _resolve_folder_path(dest_folder_path)
    file_id = _find_file(filename, src_id)
    if not file_id:
        raise FileNotFoundError(f"File '{filename}' not found in '{src_folder_path}'")
    service.files().update(
        fileId=file_id,
        addParents=dest_id,
        removeParents=src_id,
        fields="id, parents",
    ).execute()


def list_files(folder_path: str) -> list:
    """List filenames in a Drive folder path relative to DRIVE_FOLDER_ID."""
    service = _service()
    folder_id = _resolve_folder_path(folder_path)
    if not folder_id:
        return []
    query = f"'{folder_id}' in parents and trashed = false"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    return [f["name"] for f in results.get("files", [])]


# ── Internal helpers ──────────────────────────────────────────────────────────

def _find_file(name: str, parent_id: str) -> str | None:
    """Find a file by name in a specific folder. Returns file ID or None."""
    service = _service()
    query = f"name = '{name}' and '{parent_id}' in parents and trashed = false"
    results = service.files().list(q=query, fields="files(id)").execute()
    files = results.get("files", [])
    return files[0]["id"] if files else None


def _resolve_folder_path(folder_path: str) -> str | None:
    """Walk a slash-separated path under DRIVE_FOLDER_ID and return the final folder ID."""
    current_id = DRIVE_FOLDER_ID
    for part in folder_path.strip("/").split("/"):
        service = _service()
        query = (
            f"name = '{part}' and mimeType = 'application/vnd.google-apps.folder' "
            f"and '{current_id}' in parents and trashed = false"
        )
        results = service.files().list(q=query, fields="files(id)").execute()
        files = results.get("files", [])
        if not files:
            return None
        current_id = files[0]["id"]
    return current_id


def _resolve_path(file_path: str) -> str | None:
    """Resolve a full path (folders + filename) under DRIVE_FOLDER_ID to a file ID."""
    parts = file_path.strip("/").split("/")
    folder_parts = parts[:-1]
    filename = parts[-1]
    parent_id = (
        _resolve_folder_path("/".join(folder_parts)) if folder_parts else DRIVE_FOLDER_ID
    )
    if not parent_id:
        return None
    return _find_file(filename, parent_id)
